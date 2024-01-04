import streamlit as st

# This will return a dictionary of query parameters
query_params = st.experimental_get_query_params()

# Let's say the URL is something like "http://localhost:8501/?param1=value1&param2=value2"
# You can access the values like this:
param1 = query_params.get("vnp_ResponseCode", [""])[0]


def transaction_status(error_code):
    error_messages = {
        "00": "Giao dịch thành công",
        "07": "Trừ tiền thành công. Giao dịch bị nghi ngờ (liên quan tới lừa đảo, giao dịch bất thường).",
        "09": "Giao dịch không thành công do: Thẻ/Tài khoản của khách hàng chưa đăng ký dịch vụ InternetBanking tại ngân hàng.",
        "10": "Giao dịch không thành công do: Khách hàng xác thực thông tin thẻ/tài khoản không đúng quá 3 lần",
        "11": "Giao dịch không thành công do: Đã hết hạn chờ thanh toán. Xin quý khách vui lòng thực hiện lại giao dịch.",
        "12": "Giao dịch không thành công do: Thẻ/Tài khoản của khách hàng bị khóa.",
        "13": "Giao dịch không thành công do Quý khách nhập sai mật khẩu xác thực giao dịch (OTP). Xin quý khách vui lòng thực hiện lại giao dịch.",
        "24": "Giao dịch không thành công do: Khách hàng hủy giao dịch",
        "51": "Giao dịch không thành công do: Tài khoản của quý khách không đủ số dư để thực hiện giao dịch.",
        "65": "Giao dịch không thành công do: Tài khoản của Quý khách đã vượt quá hạn mức giao dịch trong ngày.",
        "75": "Ngân hàng thanh toán đang bảo trì.",
        "79": "Giao dịch không thành công do: KH nhập sai mật khẩu thanh toán quá số lần quy định. Xin quý khách vui lòng thực hiện lại giao dịch",
        "99": "Các lỗi khác (lỗi còn lại, không có trong danh sách mã lỗi đã liệt kê)",
    }
    return error_messages.get(error_code, "Mã lỗi không xác định")


# Example usage
result = transaction_status(param1)
st.write(result)  # This will print the message for error code 12
