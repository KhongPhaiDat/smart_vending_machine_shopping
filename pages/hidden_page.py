import streamlit as st
import modules.access_control as access_control


if "session_id" not in st.session_state:
    st.write(
        "Bạn đang truy cập vào trang này bằng một cách không hợp lệ. Vui lòng quét mã QR và thử lại!!!"
    )
else:
    machine_id = st.experimental_get_query_params()["id"][0]

    access_control = access_control.AccessControl(
        machine_id=machine_id, session_id=st.session_state["session_id"]
    )

    # Update VNPay session
    access_control.start_vnpay_session()
