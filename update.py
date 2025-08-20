import streamlit as st
from user_db import *

if st.session_state.get("authentication_status"):

    username = st.session_state.get("username")
    st.write(f"Logged in as: {username}")


    st.header("Contract Available")
    contract = get_active_contract()
    
    if contract:
        st.markdown(f"""
        **Contract Name:** {contract[0][1]}  
        **Length:** {contract[0][2]} months  
        **Tracks:** {contract[0][3]}  
        **Track Types:** {contract[0][4]}  
        **Base Pay:** {contract[0][5]}  
        **Salvage Terms:** {contract[0][6]}  
        **Transport Terms:** {contract[0][7]}  
        **Support Rights:** {contract[0][8]}  
        ---""")
        if st.button("Negotiate Contract"):
           if st.button("Negotiate Contract"):
            @st.dialog("negotiation")
            def negotiation():
                st.write("negotiation station")
                
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