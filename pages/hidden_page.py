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
        "Bạn đang truy cập vào trang này bằng một cách không hợp lệ. Vui lòng quét mã QR và thử lại!!!"
    )
else:
    machine_id = st.session_state["machine_id"]
    access_control = access_control.AccessControl(
        machine_id=machine_id, session_id=st.session_state["session_id"]
    )
    # Update VNPay session
    access_control.start_vnpay_session()
