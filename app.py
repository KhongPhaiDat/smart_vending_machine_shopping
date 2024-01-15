import streamlit as st
import pages.menu as menu
import uuid
import modules.access_control as access_control

# Init date_time
date_time = ""

NEW_ACCESS = 0
CONTINUE_ACCESS = 1
NO_ACCESS = 2

st.set_page_config(initial_sidebar_state="collapsed")

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>
    [data-testid="baseButton-headerNoPadding"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)


def main():
    access_decision = access_control.get_access_info()
    if access_decision == NO_ACCESS:
        st.write(
            "The machine is currently being used by another user. Please wait a moment!!!"
        )
    elif access_decision == NEW_ACCESS:
        access_control.start_user_session()
        menu.main()
    elif access_decision == CONTINUE_ACCESS:
        menu.main()


if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

try:
    machine_id = st.query_params["id"]
    if "machine_id" not in st.session_state:
        st.session_state["machine_id"] = machine_id
except:
    st.write(
        "You are accessing this page in an invalid way. Please scan the QR code and try again!!!"
    )

if "machine_id" in st.session_state:
    access_control = access_control.AccessControl(
        machine_id=machine_id, session_id=st.session_state["session_id"]
    )
    main()
