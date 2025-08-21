import streamlit as st
from user_db import *

if st.session_state.get("authentication_status"):

    username = st.session_state.get("username")
    st.write(f"Logged in as: {username}")


    st.header("Contract Available")
    contract = get_active_contract()
    
    if contract:
        st.markdown(f"""
        **Contract Name:** {contract[0][2]}  
        **Length:** {contract[0][3]} months  
        **Tracks:** {contract[0][4]}  
        **Track Types:** {contract[0][5]}  
        **Base Pay:** {contract[0][6]}%  
        **Salvage Terms:** {contract[0][7]} 
        **Transport Terms:** {contract[0][8]}%  
        **Support Rights:** {contract[0][9]}  
        **Command Rights:** {contract[0][10]}
        ---""")
        if st.button("Negotiate Contracts"):
            @st.dialog("negotiation")
            def negotiation():
                import pandas as pd
                from STlaunch import df2
                st.dataframe(
                    df2,
                    use_container_width=True,
                    column_config={
                        "Base Pay": st.column_config.NumberColumn("Base Pay", format="%.0f%%"),
                        "Transportation Terms": st.column_config.NumberColumn("Transportation Terms", format="%.0f%%"),
                    }
                )
                # Get company info for scale and reputation
                company = get_company(username)
                scale = company[4] if len(company) > 4 else 1
                reputation = company[3] if len(company) > 3 else 1
                max_rep = min(2 * scale, reputation)
                st.write(f"You may use up to {max_rep} reputation points to increase steps.")
                st.write("You may also perform up to 2 swaps: decrease a term by 2 steps to increase another by 1 step.")

                # Helper to map contract value to step number
                def value_to_step(col, value):
                    match = df2[df2[col] == value]
                    if not match.empty:
                        return int(match.iloc[0]["Step"])
                    return 1
                def step_to_value(col, step):
                    match = df2[df2["Step"] == step]
                    if not match.empty:
                        return match.iloc[0][col]
                    return None
                def valid_steps(col):
                    if col == "Transportation Terms":
                        return [int(row["Step"]) for _, row in df2.iterrows() if 5 <= int(row["Step"]) <= 9]
                    else:
                        return [int(row["Step"]) for _, row in df2.iterrows() if row[col] != "—"  and row[col] is not None and row[col] != "no"]

                # Get current contract steps (indices: 6=base_pay, 7=salvage, 8=transport, 9=support, 10=command)
                base_pay_step = value_to_step("Base Pay", contract[0][6])
                salvage_step = value_to_step("Salvage Rights", contract[0][7])
                transport_step = value_to_step("Transportation Terms", contract[0][8])
                support_step = value_to_step("Support Rights", contract[0][9])
                command_step = value_to_step("Command Rights", contract[0][10])

                # Organic swap logic: user can only increase a step if they have rep or decrease another by 2 steps
                steps = {
                    "Base Pay": base_pay_step,
                    "Salvage Rights": salvage_step,
                    "Transportation Terms": transport_step,
                    "Support Rights": support_step,
                    "Command Rights": command_step
                }
                choices = {
                    k: valid_steps(k) for k in steps
                }
                # Track rep and swaps
                rep_left = max_rep
                swap_pool = []
                new_steps = {}
                st.write("---")
                st.write("Increase a step (costs rep), or decrease a step by 2 to gain a swap (which can be used to increase another step by 1 even if out of rep). Invalid steps are not selectable.")
                # First, let user select all new steps (with only valid steps)
                temp_steps = {}
                for k in steps:
                    label = f"{k} Step (current: {steps[k]})"
                    options = choices[k]
                    # If the current step is not in options, default to the first valid option
                    if steps[k] in options:
                        default_idx = options.index(steps[k])
                    else:
                        default_idx = 0
                    temp_steps[k] = st.selectbox(label, options, index=default_idx)

                # Now, calculate total rep and swaps needed
                rep_needed = 0
                swap_needed = 0
                swap_gained = 0
                for k in steps:
                    diff = temp_steps[k] - steps[k]
                    if diff > 0:
                        rep_needed += diff
                    elif diff < 0 and abs(diff) == 2:
                        swap_gained += 1
                # If rep_needed > max_rep, try to use swaps
                swap_needed = max(0, rep_needed - max_rep)
                can_submit = (swap_needed <= swap_gained)
                rep_left = max(0, max_rep - rep_needed + swap_gained)
                new_steps = temp_steps
                st.write(f"Reputation needed: {rep_needed} / {max_rep}")
                st.write(f"Swaps needed: {swap_needed}, Swaps gained: {swap_gained}")
                st.write("---")
                st.write("**Negotiated Steps Preview:**")
                for col in ["Base Pay", "Salvage Rights", "Transportation Terms", "Support Rights", "Command Rights"]:
                    st.write(f"{col}: Step {new_steps[col]} → {step_to_value(col, new_steps[col])}")
                if st.button("Submit Negotiation", disabled=not can_submit, key="submit_negotiation"):
                    # Set all previous contracts for this owner to inactive
                    import user_db
                    user_db.set_all_contracts_inactive()
                    # Add new contract for this company/user
                    add_contract(
                        username,
                        contract[0][1],  # name
                        contract[0][2],  # length
                        contract[0][3],  # tracks
                        contract[0][4],  # track_types
                        step_to_value("Base Pay", new_steps["Base Pay"]),
                        step_to_value("Salvage Rights", new_steps["Salvage Rights"]),
                        step_to_value("Transportation Terms", new_steps["Transportation Terms"]),
                        step_to_value("Support Rights", new_steps["Support Rights"]),
                        step_to_value("Command Rights", new_steps["Command Rights"]),
                        status='active'
                    )
                    st.success("Negotiation submitted!")
                if not can_submit:
                    st.warning("You have exceeded your allowed reputation for negotiation or made an invalid selection. (You can decrease a term by 2 steps to gain a swap.)")
                st.write(f"Reputation left: {rep_left}")
                st.write(f"Swaps available: {len(swap_pool)} (decrease a term by 2 steps to gain a swap)")
                st.write("---")
                st.write("**Negotiated Steps Preview:**")
                for col in ["Base Pay", "Salvage Rights", "Transportation Terms", "Support Rights", "Command Rights"]:
                    st.write(f"{col}: Step {new_steps[col]} → {step_to_value(col, new_steps[col])}")
                can_submit = rep_left >= 0
                if st.button("Submit Negotiation", disabled=not can_submit):
                    update_contract(
                        contract[0][0],
                        base_pay=step_to_value("Base Pay", new_steps["Base Pay"]),
                        salvage_terms=step_to_value("Salvage Rights", new_steps["Salvage Rights"]),
                        transport_terms=step_to_value("Transportation Terms", new_steps["Transportation Terms"]),
                        support_rights=step_to_value("Support Rights", new_steps["Support Rights"]),
                        command_rights=step_to_value("Command Rights", new_steps["Command Rights"])
                    )
                    st.success("Negotiation submitted!")
                if not can_submit:
                    st.warning("You have exceeded your allowed reputation for negotiation or made an invalid selection.")
            negotiation()
            st.success("Contract accepted!")
    else:
        st.info("No active contract available.")

    if company_exists(st.session_state["username"]):
        company = get_company(st.session_state["username"])
        st.write(f"Your company: {company[0]}")
        st.write(f"Support Points: {company[1]}")
        st.write(f"Reputation: {company[3]}")


    get_pilots = get_pilots(st.session_state["username"])
    st.write("Your pilots:")
    for each in get_pilots:
        st.write(f"{each[1]} (Callsign: {each[2]}, Skill: {each[3]}/{each[4]})")
        st.button(f"Upgrade {each[1]}", key=f"edit_{each[0]}")
        st.button(f"Heal {each[1]}", key=f"heal_{each[0]}")


    mechs = get_mechs(st.session_state["username"])
    if mechs:
        st.write("Your mechs:")
        for mech in mechs:
            # mech = (id, name, bv, tonnage)
            st.write(f"{mech[1]} (BV: {mech[2]}, Tonnage: {mech[3]})")
            if st.button(f"Repair {mech[1]}", key=f"repair_{mech[0]}"):
                @st.dialog("Repair")
                def repair_mech_dialog():
                    rChoice = st.selectbox("Select repair option:", ["Armor damage only", "Structure and/or critical damage", "Crippled", "Destroyed"])
                    if st.button("Confirm Repair"):
                        st.write(f"Repairing {mech[1]} with option: {rChoice}")
                repair_mech_dialog()
else:
    st.warning("You are not logged in.")