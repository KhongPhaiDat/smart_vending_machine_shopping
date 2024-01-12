import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pages.menu as menu
import hashlib
import hmac
from datetime import datetime
import urllib.parse
from streamlit.components.v1 import html
import time
from zoneinfo import ZoneInfo
from decimal import Decimal
import boto3

secret_key = "NRVNGGEOFCMRHZCLIRCUBYILIGPDRQKF"
timezone = ZoneInfo("Asia/Ho_Chi_Minh")


def get_machine_info():
    return st.session_state["machine_info"]


def get_item_new_quantity():
    return st.session_state["item_new_quantity"]


def open_page(url):
    open_script = """
        <script type="text/javascript">
            window.open('%s', '_blank').focus();
        </script>
    """ % (
        url
    )
    html(open_script)


# Show total price
def show_total_price():
    st.write(
        "Total Price: ",
        menu.calculate_total_price(get_machine_info(), get_item_new_quantity()),
    )


payment_methods = ["Vui lòng chọn", "VN Pay"]


# Show payment method
def show_payment_method():
    chosen_method = st.selectbox("Choose a payment method: ", payment_methods)
    return chosen_method


def hmacsha512(key, data):
    byteKey = key.encode("utf-8")
    byteData = data.encode("utf-8")
    return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()


#  prepare data to send to API
def prepare_data(status):
    vnp_Version = "2.1.0"
    vnp_Command = "pay"
    vnp_TmnCode = "SMXX9OJQ"
    vnp_Amount = str(
        menu.calculate_total_price(get_machine_info(), get_item_new_quantity()) * 100
    )
    # vnp_BankCode = ""
    vnp_CreateDate = "20240104095959"
    vnp_CurrCode = "VND"
    vnp_IpAddr = "113.161.0.216"
    vnp_Locale = "vn"
    vnp_OrderInfo = f"Đơn hàng tạo bởi máy {get_machine_info()['id']}"
    vnp_OrderType = "other"
    vnp_ReturnUrl = "https://svm.datluyendevops.online/checkout"
    # vnp_ReturnUrl = "http://localhost:8501/checkout"

    if status == 0:
        menu.date_time = datetime.now(timezone).strftime("%Y%m%d%H%M%S")

    vnp_TxnRef = menu.date_time + str(get_machine_info()["id"])
    requestData = dict()
    requestData["vnp_Version"] = vnp_Version
    requestData["vnp_Command"] = vnp_Command
    requestData["vnp_TmnCode"] = vnp_TmnCode
    requestData["vnp_Amount"] = vnp_Amount
    requestData["vnp_CreateDate"] = menu.date_time
    requestData["vnp_CurrCode"] = vnp_CurrCode
    requestData["vnp_IpAddr"] = vnp_IpAddr
    requestData["vnp_Locale"] = vnp_Locale
    requestData["vnp_OrderInfo"] = vnp_OrderInfo
    requestData["vnp_OrderType"] = vnp_OrderType
    requestData["vnp_ReturnUrl"] = vnp_ReturnUrl
    requestData["vnp_TxnRef"] = vnp_TxnRef
    return requestData


# Create order and send to VNPAY.
def create_order():
    requestData = prepare_data(1)
    inputData = sorted(requestData.items())
    queryString = ""
    seq = 0
    for key, val in inputData:
        if seq == 1:
            queryString = (
                queryString + "&" + key + "=" + urllib.parse.quote_plus(str(val))
            )
        else:
            seq = 1
            queryString = key + "=" + urllib.parse.quote_plus(str(val))

    vnp_SecureHash = hmacsha512(secret_key, queryString)
    url = (
        "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
        + "?"
        + queryString
        + "&vnp_SecureHash="
        + vnp_SecureHash
    )
    return url


def collect_order_info():
    message = dict()
    # requestData["vnp_TxnRef"] is the ORDER Key
    globalRequestData = prepare_data(0)
    message[str(globalRequestData["vnp_TxnRef"])] = dict()

    # Get updated machine_info
    machine_info = get_machine_info()

    # Update quantity from user
    for item_name, value in get_item_new_quantity().items():
        machine_info["items"][item_name]["amount"] = Decimal(value)

    # get_machine_info()['id'] is the id of vending machine
    message[str(globalRequestData["vnp_TxnRef"])]["vending_machine_id"] = machine_info[
        "id"
    ]

    # Add items info
    message[str(globalRequestData["vnp_TxnRef"])]["items"] = dict()
    items = machine_info["items"]

    for item_name, item_properties in items.items():
        message[str(globalRequestData["vnp_TxnRef"])]["items"][str(item_name)] = {
            "price": item_properties["price"],
            "quantity": item_properties["amount"],
            "cost": item_properties["price"] * item_properties["amount"],
        }

    # Add total cost
    message[str(globalRequestData["vnp_TxnRef"])][
        "total_price"
    ] = menu.calculate_total_price(get_machine_info(), get_item_new_quantity())
    message[str(globalRequestData["vnp_TxnRef"])]["transaction_status_code"] = ""
    return message


# Show pay button
def show_pay_button():
    st.warning("Please choose your payment method!")
    st.warning("If you want to cancel, please press CANCEL button below!")
    chosen_method = show_payment_method()
    if st.button("Pay"):
        write_order_to_tmp_database()
        if chosen_method == "VN Pay":
            url = create_order()
            open_page(url)
            time.sleep(2)
            switch_page("hidden_page")
        elif chosen_method == "Vui lòng chọn":
            st.write("Hãy chọn phương thức thanh toán")


# Show cancel button
def show_cancel_button():
    if st.button("Cancel"):
        switch_page("cancel")


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

    return new_message


def write_order_to_DB(orders):
    dynamoDB_client = boto3.client("dynamodb", region_name="ap-northeast-1")
    message = reformat_message(orders)

    response = dynamoDB_client.put_item(Item=message, TableName="order_history")
    return response


# Write order to tmp database
def write_order_to_tmp_database():
    orders = collect_order_info()
    write_order_to_DB(orders)


def main():
    if "session_id" not in st.session_state:
        st.write(
            "Bạn đang truy cập vào trang này bằng một cách không hợp lệ. Vui lòng quét mã QR và thử lại!!!"
        )
    else:
        show_total_price()
        show_pay_button()
        show_cancel_button()


if __name__ == "__main__":
    main()
