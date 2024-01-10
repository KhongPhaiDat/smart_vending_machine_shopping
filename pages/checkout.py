import streamlit as st
import pages.payment_page as payment_page
import boto3
import requests
import json


# reformat message to match dynamoDB
def reformat_message(message):
    new_message = dict()

    key = ""
    for a, _ in message.items():
        if key == "":
            key = a
            break

    new_message = {"order": {"S": str(key)}}

    new_message["vending_machine_id"] = {"S": message[str(key)]["vending_machine_id"]}

    new_message["items"] = {"M": dict()}
    new_message["items"]["M"] = dict()

    for name, value in message[key]["items"].items():
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
def add_to_database(message, response):
    dynamoDB_client = boto3.client("dynamodb", region_name="ap-northeast-1")

    message = reformat_message(message)
    message["transaction_status_code"] = {"S": str(response)}

    # st.write("Djt me FPT")
    response = dynamoDB_client.put_item(Item=message, TableName="order_history")
    # st.write(response)
    return response


# return status code
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


# get order_key after checking out successfully
def get_order_key():
    order_key = st.experimental_get_query_params()["vnp_TxnRef"][0]
    return order_key


# retrieve order from "order_history" base on order_key
def get_order_from_database_based_on_key():
    dynamoDB = boto3.resource("dynamodb", region_name="ap-northeast-1")
    table = dynamoDB.Table("order_history")
    order_key = get_order_key()
    response = table.get_item(Key={"order": order_key})
    # st.write(response)
    return response["Item"]["items"]


# return response
response = st.experimental_get_query_params()["vnp_ResponseCode"][0]
return_status(response)

# push order to database to  "order_history" database
order_message = payment_page.collect_order_info()
add_to_database(order_message, response)

# get order list from database based on order key
order_response = get_order_from_database_based_on_key()
st.write(order_response)


# get machine id
def get_machine_id():
    dynamoDB = boto3.resource("dynamodb", region_name="ap-northeast-1")
    table = dynamoDB.Table("order_history")
    order_key = get_order_key()
    response = table.get_item(Key={"order": order_key})
    machine_id = response["Item"]["vending_machine_id"]
    return machine_id


# create release message
def create_release_message(machine_id, order_list):
    message = dict()
    # Message is Json {
    #     'machine_id': machine_id,
    #     'order_list': order_list
    # }

    message = {"machine_id": machine_id, "order_list": order_list}
    return message


# define URL dictionary
def get_url_dictionary():
    vending_URL_repository = dict()

    vending_URL_repository[
        "ua3dXFyQwMSMzvzEC"
    ] = "https://ozkhtpzc54m7jzgngyw4ent5cu0fojgr.lambda-url.ap-northeast-1.on.aws/"

    return vending_URL_repository


# Get corresponding machine ID URL
def mapping_machine_to_lambda_URL(machine_id):
    data_url = get_url_dictionary()
    return data_url[machine_id]


# send request to vending machine id
def send_request_to_vending_machine_id(machine_id, message):
    lambda_url = mapping_machine_to_lambda_URL(machine_id)
    response = requests.post(lambda_url, data=message)

    return response


# send message to
if response == "00":
    machine_id = get_machine_id()
    order_list = get_order_from_database_based_on_key()
    message = create_release_message(machine_id, order_list)
    lambda_response = send_request_to_vending_machine_id(machine_id, message)

    st.write(lambda_response.text)
