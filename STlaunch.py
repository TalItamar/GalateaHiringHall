import yaml
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)
from user_db import *
import datetime
import pandas as pd



rows = [
    # Step, Base Pay %, Command Rights, Salvage Rights,   Support Rights,    Transportation Terms %
    (1,   50,  "—",           "None",                "None",             None),
    (2,   55,  "—",           "—",                   "Straight/20%",     None),
    (3,   60,  "Integrated",  "Exchange",            "Straight/40%",     None),
    (4,   70,  "—",           "10%",                 "Straight/60%",     None),
    (5,   80,  "—",           "20%",                 "Straight/80%",     0),
    (6,   90,  "—",           "30%",                 "Straight/100%",    25),
    (7,   100, "House",       "40%",                 "Battle/10%",       50),
    (8,   110, "Liaison",     "50%",                 "Battle/20%",       75),
    (9,   120, "—",           "60%",                 "Battle/30%",       100),
    (10,  130, "—",           "70%",                 "Battle/40%",       None),
    (11,  150, "Independent", "80%",                 "Battle/50%",       None),
    (12,  175, "—",           "90%",                 "Battle/75%",       None),
    (13,  200, "—",           "100%",                "Battle/100%",      None),
]

df2 = pd.DataFrame(rows, columns=[
    "Step", "Base Pay", "Command Rights", "Salvage Rights", "Support Rights", "Transportation Terms"
])


#load mercenary mech MUL CSV
df = pd.read_csv("MercenaryMUL.csv")
#turn into options for mech selection
options = [f"{row[0]}  |BV: {row[3]} |Tonnage: {row[2]}" for _, row in df.iterrows()]

# Loading config file
with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)
init_db()

# Creating the authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)
st.write("""#  Welcome One and All! 
         to setup register with your mercenary company as your username!""")
# authenticator = stauth.Authenticate(
#     '../config.yaml'
# )

# Creating a login widget
try:
    authenticator.login()
except LoginError as e:
    st.error(e)
user_info = config['credentials']['usernames'].get(st.session_state["username"], {})
roles = user_info.get('roles') or []
if st.session_state["authentication_status"] and "admin" in roles:
    st.write('Welcome Hiring Hall Administrator')

    st.header("Contract Submission")
    if st.button("Submit Contract"):
        @st.dialog("Submit Contract")
        def submit_contract_dialog():
            name = st.text_input("Contract Name:")
            length = st.number_input("Contract Length (in monthes):", min_value=1)
            tracks = st.text_input("Tracks (comma-separated):")
            track_types = st.text_input("Track Types (comma-separated):")
            base_pay = st.number_input("Base Pay:", min_value=0)
            salvage_terms = st.number_input("Salvage Terms:", min_value=0)

            st.dataframe(
    df,
    use_container_width=True,
    column_config={
        "Base Pay": st.column_config.NumberColumn("Base Pay", format="%.0f%%"),
        "Transportation Terms": st.column_config.NumberColumn("Transportation Terms", format="%.0f%%"),
    }
)

# Step picker + details
            step = st.selectbox("Pick a step", df2["Step"].tolist(), index=0)
            row = df2.loc[df2["Step"] == step].iloc[0]

            st.write("**Selected Step Details:**")
            st.write(f"**Base Pay:** {row['Base Pay']}%")
            st.write(f"**Command Rights:** {row['Command Rights']}")
            st.write(f"**Salvage Rights:** {row['Salvage Rights']}")
            st.write(f"**Support Rights:** {row['Support Rights']}")
            st.write(f"**Transportation Terms:** {row['Transportation Terms']}%")
            transport_terms = st.number_input("Transport Terms:", min_value=0)
            support_rights = st.number_input("Support Rights:", min_value=0)
            if st.button("Submit"):
                set_all_contracts_inactive()
                add_contract(name, length, tracks, track_types, base_pay, salvage_terms, transport_terms, support_rights)
                st.success("Contract submitted successfully!")
        submit_contract_dialog()

    companies = get_all_companies()
    for company in companies:
        st.subheader(f"Company: {company[1]} (Owner: {company[5]})")
        st.markdown("**Pilots:**")
        pilots = get_pilots(company[5])
        for pilot in pilots:
            with st.expander(f"Edit Pilot: {pilot[1]} ({pilot[2]})"):  # pilot[1]=name, pilot[2]=callsign
                new_name = st.text_input("Pilot Name", value=pilot[1], key=f"pilot_name_{pilot[0]}")
                new_callsign = st.text_input("Callsign", value=pilot[2], key=f"pilot_callsign_{pilot[0]}")
                new_pskill = st.number_input("Pskill", value=int(pilot[3]), min_value=0, max_value=6, step=1, key=f"pilot_pskill_{pilot[0]}")
                new_gskill = st.number_input("Gskill", value=int(pilot[4]), min_value=0, max_value=6, step=1, key=f"pilot_gskill_{pilot[0]}")
                if st.button("Update Pilot", key=f"update_pilot_{pilot[0]}"):
                    update_pilot(pilot[0], name=new_name, callsign=new_callsign, Pskill=new_pskill, Gskill=new_gskill)
                    st.success("Pilot updated!")
        if st.button("Edit Company", key=f"edit_{company[0]}"):
            @st.dialog("Edit Company")
            def edit_company_dialog():
                st.write("Edit Company Details")
                new_name = st.text_input("New Company Name:", value=company[1])
                new_support_points = st.number_input("New Support Points:", value=company[2])
                new_reputation = st.number_input("New Reputation:", value=company[4])
                if st.button("Save Changes"):
                    update_company(company[0], new_name, new_support_points, new_reputation)
                    st.success("Company details updated successfully!")
            edit_company_dialog()
        if st.button("Edit Mechs", key=f"edit_mechs_{company[0]}"):
            @st.dialog("Edit Mechs")
            def edit_mech_dialog():
                mechs = get_all_mechs()
                if not mechs:
                    st.info("No mechs available.")
                    return
                mech_options = {f"{m[2]} (User: {m[1]}, BV: {m[3]}, Tonnage: {m[4]})": m for m in mechs}
                selected = st.selectbox("Select a mech to edit", list(mech_options.keys()), key="edit_mech_select")
                mech = mech_options[selected]
                new_name = st.text_input("Mech Name", value=mech[2], key="edit_mech_name")
                new_bv = st.number_input("Battle Value", value=int(mech[3]), step=1, key="edit_mech_bv")
                new_tonnage = st.number_input("Tonnage", value=int(mech[4]), step=1, key="edit_mech_tonnage")
                if st.button("Update Mech", key="update_mech_btn"):
                    update_mech(mech[0], name=new_name, bv=new_bv, tonnage=new_tonnage)
                    st.success("Mech updated!")
            edit_mech_dialog()
    authenticator.logout()

elif st.session_state["authentication_status"]:
    st.write('___')
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["username"]}*!')
    # Get user info from config
    email = user_info.get('email', '')
    roles_str = ','.join(roles)
    add_user(st.session_state["username"], user_info.get('first_name', ''), email, roles_str)
    now = datetime.datetime.now().isoformat()
    update_last_login(st.session_state["username"], now)
    user_db_info = get_user(st.session_state["username"])
    # st.write(f"User info from DB: {user_db_info}")# print user info

    st.title("Company HQ")
    if company_exists(st.session_state["username"]):
        company = get_company(st.session_state["username"])
        st.write(f"Your company: {company[0]}")
        st.write(f"Support Points: {company[1]}")
        st.write(f"Reputation: {company[3]}")


        st.title('Barracks')
        get_pilots = get_pilots(st.session_state["username"])
        st.write("Your pilots:")
        for each in get_pilots:
            st.write(f"{each[1]} (Callsign: {each[2]}, Skill: {each[3]}/{each[4]})")
        if st.button('Hire Pilot'):
            @st.dialog("Pilot Hiring")
            def hire_pilot_dialog():
                st.write("What is the pilots name, callsign, and base skill")
                Pname = st.text_input('Pilot Name:')
                Cname = st.text_input('Callsign:')
                rookieOr = st.toggle("Rookie or Regular")
                if not rookieOr:
                    st.write("Pilot Intern 5/6 skill, no BV cost they're doing it 'for the exposure'")
                else:
                    st.write("Regular pilot 4/5 skill, 100 BV")
                if st.button('Hire'):
                    if not Pname or not Cname:
                        st.warning("Please fill in all fields!")
                    else:
                        st.write(f"Pilot {Pname} with callsign {Cname} hired!")
                        add_pilot(st.session_state["username"], Pname, Cname, 5 if rookieOr else 4, 6 if rookieOr else 5)
                        update_support_points(st.session_state["username"], int(company[1]) - (0 if rookieOr else 100))
                        st.rerun()
            if hire_pilot_dialog():
                st.write("Pilot hired successfully!")

        st.title('Mechbay') 
        selected = st.selectbox('Select a mech from the list:', options, key='mech_select')
        if st.button('Buy mech'):
            row = df.iloc[options.index(selected)]
            add_mech(st.session_state["username"], row[0], int(row[3].replace(',', '')), int(row[2]))
            update_support_points(st.session_state["username"], int(company[1]) - (int(row[3].replace(',', ''))))
            st.write(f'Mech {row[0]} purchased, good luck mercenary!')

        
        mechs = get_mechs(st.session_state["username"])
        if mechs:
            st.write("Your mechs:")
            for mech in mechs:
                # mech = (id, name, bv, tonnage)
                st.write(f"- {mech[1]} (BV: {mech[2]}, Tonnage: {mech[3]})")
                action = st.selectbox('Select an action:', ['View Details', 'Sell Mech'], key=f"{mech[0]}_{mech[1]}")
                if action == 'View Details':
                    st.write(f"Viewing details for {mech[1]}")
                elif action == 'Sell Mech':
                    st.write(f"Selling {mech[1]}")
                    remove_mech(st.session_state["username"], mech[0])
                    update_support_points(st.session_state["username"], (int(company[1]) + (int(mech[2])/2)))
                    st.write(f"Mech {mech[1]} sold for {int(mech[2])/2} support points!")
                    st.rerun()

    else:
        Cname = st.text_input('Company name:')
        Csupport = st.number_input('Support Points:', 0, format="%d")
        Creputation = st.number_input('Reputation:', 0, format="%d")
        if st.button('Create Company'):
            add_company(Cname, Csupport, '', Creputation, st.session_state["username"])



elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')


if st.session_state["authentication_status"] is None:
# Creating a password reset widget
    if st.session_state["authentication_status"]:
        try:
            if authenticator.reset_password(st.session_state["username"]):
                st.success('Password modified successfully')
                config['credentials']['usernames'][username_of_forgotten_password]['pp'] = new_random_password
        except ResetError as e:
            st.error(e)
        except CredentialsError as e:
            st.error(e)
        st.write('_If you use the password reset widget please revert the password to what it was before once you are done._')

# Creating a new user registration widget

    try:
        (email_of_registered_user,
        username_of_registered_user,
        name_of_registered_user) = authenticator.register_user()
        if email_of_registered_user:
            st.success('User registered successfully')
    except RegisterError as e:
        st.error(e)

    # Creating a forgot password widget
    try:
        (username_of_forgotten_password,
        email_of_forgotten_password,
        new_random_password) = authenticator.forgot_password()
        if username_of_forgotten_password:
            st.success(f"New password **'{new_random_password}'** to be sent to user securely")
            config['credentials']['usernames'][username_of_forgotten_password]['pp'] = new_random_password
            # Random password to be transferred to the user securely
        elif not username_of_forgotten_password:
            st.error('Username not found')
    except ForgotError as e:
        st.error(e)

    # Creating a forgot username widget
    try:
        (username_of_forgotten_username,
        email_of_forgotten_username) = authenticator.forgot_username()
        if username_of_forgotten_username:
            st.success(f"Username **'{username_of_forgotten_username}'** to be sent to user securely")
            # Username to be transferred to the user securely
        elif not username_of_forgotten_username:
            st.error('Email not found')
    except ForgotError as e:
        st.error(e)

    # Creating an update user details widget
    if st.session_state["authentication_status"]:
        try:
            if authenticator.update_user_details(st.session_state["username"]):
                st.success('Entries updated successfully')
        except UpdateError as e:
            st.error(e)

# Saving config file
with open('config.yaml', 'w', encoding='utf-8') as file:
    yaml.dump(config, file, default_flow_style=False)