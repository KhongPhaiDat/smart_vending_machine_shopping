import streamlit as st
import modules.access_control as access_control

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

if "session_id" not in st.session_state and "machine_id" not in st.session_state:
    st.write(
        "You are accessing this page in an invalid way. Please scan the QR code and try again!!!"
    )
else:
    machine_id = st.session_state["machine_id"]
    access_control = access_control.AccessControl(
        machine_id=machine_id, session_id=st.session_state["session_id"]
    )
    # Update VNPay session
    access_control.start_vnpay_session()
