import streamlit as st

from modules.access_control import AccessControl

st.write("Vui lòng SCAN QR để thực hiện lại giao dịch")
machine_id = st.session_state["machine_id"]
access_control = AccessControl(machine_id)
access_control.end_user_session()
