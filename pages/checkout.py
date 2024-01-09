import streamlit as st
import pages.payment_page as payment_page
import boto3


# reformat message to match dynamoDB
def reformat_message(message):
    new_message = dict()

    key = ""
    for a, _ in message.items():
        if key == "":
            key = a
            break

    new_message = {"order": {"S": "ua3dXFyQwMSMzvzEC"}}

    new_message["vending_machine_id"] = {"S": message[key]["vending_machine_id"]}

    new_message["items"] = {"M": dict()}

    for name, value in message[key]["items"].items():
        new_message["items"]["M"] = {str(name): dict()}
        new_message["items"]["M"][str(name)] = {"M": dict()}
        new_message["items"]["M"][str(name)]["M"]["price"] = {"N": str(value["price"])}
        new_message["items"]["M"][str(name)]["M"]["quantity"] = {
            "N": str(value["quantity"])
        }
        new_message["items"]["M"][str(name)]["M"]["cost"] = {"N": str(value["cost"])}
    new_message["total_price"] = {"N": str(message[key]["total_price"])}
    new_message["transaction_status_code"] = {
        "S": str(message[key]["transaction_status_code"])
    }

    return new_message


# prepare dynamoDB to push data
def add_to_database(message):
    dynamoDB_client = boto3.client("dynamodb", region_name="ap-northeast-1")
    table_name = "order_history"

    message = reformat_message(message)

    response = dynamoDB_client.put_item(Item=message, TableName="order_history")
    return response


def return_status(error):
    status = {
        "00": "Giao dịch thành công",  # Successful transaction
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

    error_solve = status.get(error, "Lỗi không xác định")

    if error == "00":
        st.write("Giao dịch thành công! Vui lòng chờ lấy hàng")
    else:
        st.write("Giao dịch không thành công")
        st.write(error_solve + " " + status[error])


response = st.experimental_get_query_params()["vnp_ResponseCode"][0]
return_status(response)
