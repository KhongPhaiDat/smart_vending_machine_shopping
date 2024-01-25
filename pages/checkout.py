from decimal import Decimal
import json
from time import sleep
from modules.access_control import AccessControl
from modules.release_control import ReleaseControl
import streamlit as st
import pages.payment_page as payment_page
import modules.menu_component as menu_component
import boto3
import requests


# reformat message to match dynamoDB
def reformat_message(message):
    new_message = dict()
    key = ""
    for a, _ in message.items():
        if key == "":
            key = a
            break
    # st.write("Reformat: ", message)
    new_message = {"order": {"S": message["order"]}}
    new_message["vending_machine_id"] = {"S": message["vending_machine_id"]}
    # new_message["vending_machine_id"] = {"S": message[str(key)]["vending_machine_id"]}
    new_message["items"] = {"M": dict()}
    new_message["items"]["M"] = dict()
    for name, value in message["items"].items():
        new_message["items"]["M"][str(name)] = {"M": dict()}
        new_message["items"]["M"][str(name)]["M"]["price"] = {
            "N": str(value["price"])}
        new_message["items"]["M"][str(name)]["M"]["quantity"] = {
            "N": str(value["quantity"])
        }
        new_message["items"]["M"][str(name)]["M"]["cost"] = {
            "N": str(value["cost"])}
    new_message["total_price"] = {"N": str(message["total_price"])}
    new_message["transaction_status_code"] = {
        "S": str(message["transaction_status_code"])
    }

    return new_message


# prepare dynamoDB to push data
def add_to_database(message, response):
    dynamoDB_client = boto3.client("dynamodb", region_name="ap-northeast-1")
    message = reformat_message(message)
    message["transaction_status_code"] = {"S": str(response)}
    response = dynamoDB_client.put_item(
        Item=message, TableName="order_history")
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
        "15": "Lỗi gì đó chưa biết! Nếu gặp thì phản hồi cho bên phát triển phần mềm!",
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
        st.write(error_solve)


# get order_key after checking out successfully
def get_order_key():
    order_key = st.query_params["vnp_TxnRef"]
    return order_key


# retrieve order from "order_history" base on order_key
def get_order_from_database_based_on_key():
    dynamoDB = boto3.resource("dynamodb", region_name="ap-northeast-1")
    table = dynamoDB.Table("order_history")
    order_key = get_order_key()
    response = table.get_item(Key={"order": order_key})
    return response["Item"]["items"]


# get machine id
def get_machine_id():
    dynamoDB = boto3.resource("dynamodb", region_name="ap-northeast-1")
    table = dynamoDB.Table("order_history")
    order_key = get_order_key()
    response = table.get_item(Key={"order": order_key})
    machine_id = response["Item"]["vending_machine_id"]
    return machine_id


def decimal2int(message):
    new_message = dict()
    for key, value in message.items():
        if isinstance(value, dict):
            new_message[key] = decimal2int(value)
        elif isinstance(value, Decimal):
            new_message[key] = int(value)
        else:
            new_message[key] = value
    return new_message

# create release message


def create_release_message(machine_id, order_list):
    message = dict()
    order_list = decimal2int(message=order_list)
    message = {"machine_id": machine_id, "order_list": order_list}
    return message


# define URL dictionary
def get_url_dictionary():
    vending_URL_repository = dict()
    vending_URL_repository[
        "ua3dXFyQwMSMzvzEC"
    ] = "https://dhry3vb4qmez3g7dgzb6gvdtte0bsipr.lambda-url.ap-southeast-1.on.aws/"

    vending_URL_repository[
        "123456"
    ] = "https://ozkhtpzc54m7jzgngyw4ent5cu0fojgr.lambda-url.ap-northeast-1.on.aws/"

    return vending_URL_repository


# Get corresponding machine ID URL
def mapping_machine_to_lambda_URL(machine_id):
    data_url = get_url_dictionary()
    return data_url[machine_id]


# send request to vending machine id
def send_request_to_vending_machine_id(machine_id, message):
    lambda_url = mapping_machine_to_lambda_URL(machine_id)
    response = requests.post(lambda_url, json=message)
    return response


# get origin
def get_origin_item_list(machine_id):
    menu = menu_component.MenuComponent()
    origin_item_list = menu.queryMenuByMachineIDFromDatabase(machine_id)
    return origin_item_list


def order_list_to_dict(order_list):
    items = dict()
    for item_name, value in order_list.items():
        items[item_name] = {
            "amount": int(value["quantity"]),
            "price": int(value["price"]),
        }
    return items


def orgin_item_list_to_dict(origin_item_list):
    items = dict()
    for item_name, value in origin_item_list["items"].items():
        items[item_name] = {
            "amount": int(value["amount"]),
            "price": int(value["price"]),
        }
    return items


def subtract_from_order_list(origin_item_list, order_list):
    reformat_order_list = order_list_to_dict(order_list)
    reformat_origin_list = orgin_item_list_to_dict(origin_item_list)
    subtracted_item_list = dict()
    for key in reformat_order_list.keys():
        subtracted_item_list[key] = dict()
        subtracted_item_list[key]["amount"] = (
            reformat_origin_list[key]["amount"] -
            reformat_order_list[key]["amount"]
        )
        subtracted_item_list[key]["price"] = reformat_order_list[key]["price"]
    return subtracted_item_list


def create_updated_item_message(machine_id, updated_item_list):
    message = {"id": {"S": str(machine_id)}}
    message["items"] = {"M": dict()}
    message["items"]["M"] = dict()
    for name, value in updated_item_list.items():
        message["items"]["M"][str(name)] = {"M": dict()}
        message["items"]["M"][str(name)]["M"]["price"] = {
            "N": str(value["price"])}
        message["items"]["M"][str(name)]["M"]["amount"] = {
            "N": str(value["amount"])}
    return message


def update_item_list_to_database(updated_item_message):
    dynamoDB_client = boto3.client("dynamodb", region_name="ap-northeast-1")
    response = dynamoDB_client.put_item(
        TableName="Menu_database", Item=updated_item_message
    )
    return response


# update item list in database
def update_item_list_in_database(machine_id, order_list):
    origin_item_list = get_origin_item_list(machine_id)
    updated_item_list = subtract_from_order_list(origin_item_list, order_list)
    updated_item_message = create_updated_item_message(
        machine_id, updated_item_list)
    update_item_list_to_database(updated_item_message)


# return transaction status
def get_transaction_status():
    transaction_status = st.query_params["vnp_ResponseCode"]
    return transaction_status


def get_order_from_DB(order_key):
    dynamoDB = boto3.resource("dynamodb", region_name="ap-northeast-1")
    table = dynamoDB.Table("order_history")
    response = table.get_item(Key={"order": order_key})
    return response["Item"]


def add_transaction_status_to_order(order_data, transaction_status):
    order_data["transaction_status_code"] = {"S": str(transaction_status)}
    return order_data


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

# print transaction status
return_status(get_transaction_status())

# push order to database to  "order_history" database
transaction_status = get_transaction_status()
order_key = get_order_key()
order_data = get_order_from_DB(order_key)
order_message = add_transaction_status_to_order(order_data, transaction_status)
add_to_database(order_message, transaction_status)

# get order list from database based on order key
order_response = get_order_from_database_based_on_key()
machine_id = get_machine_id()

# send message to
if get_transaction_status() == "00":
    release_control = ReleaseControl(get_order_key())
    if release_control.is_order_not_released():
        order_list = get_order_from_database_based_on_key()
        message = create_release_message(machine_id, order_list)
        lambda_response = send_request_to_vending_machine_id(
            machine_id, message)

        if lambda_response.status_code == 200:
            update_item_list_in_database(machine_id, order_list)
            release_control.update_order_release_status()
            st.write(
                "Xuất hàng thành công! Nếu có sự cố, vui lòng liên hệ nhân viên!!!")
        else:
            st.write(lambda_response)
    else:
        st.write("Bú một lần thôi. Bú lắm thế")


# update access lock to release lock
access_control = AccessControl(machine_id)
access_control.end_user_session()
