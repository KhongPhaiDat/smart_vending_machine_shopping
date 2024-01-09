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


secret_key = "NRVNGGEOFCMRHZCLIRCUBYILIGPDRQKF"

timezone = ZoneInfo("Asia/Ho_Chi_Minh")


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
    st.write("Total Price: ", menu.calculate_total_price())


payment_methods = ["Vui lòng chọn", "VN Pay", "Ngân Lượng Wallet", "PayPal"]
api_url = ""


# Show payment method
def show_payment_method():
    chosen_method = st.selectbox("Choose a payment method: ", payment_methods)
    return chosen_method


# Redirect to Ngân Lượng Checkout URL
def ngan_luong_check_out():
    url = "https://www.nganluong.vn/checkout"

    # webbrowser.open_new(url)


def hmacsha512(key, data):
    byteKey = key.encode("utf-8")
    byteData = data.encode("utf-8")
    return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


#  prepare data to send to API
def prepare_data(status):
    vnp_Version = "2.1.0"
    vnp_Command = "pay"
    vnp_TmnCode = "SMXX9OJQ"
    vnp_Amount = str(menu.calculate_total_price() * 100)
    # vnp_BankCode = ""
    vnp_CreateDate = "20240104095959"
    vnp_CurrCode = "VND"
    vnp_IpAddr = "113.161.0.216"
    vnp_Locale = "vn"
    vnp_OrderInfo = f"Đơn hàng tạo bởi máy {menu.machine_info['id']}"
    vnp_OrderType = "other"
    vnp_ReturnUrl = "https://svm.datluyendevops.online/checkout"
    # vnp_ReturnUrl = "http://localhost:8501/checkout"

    if status == 0:
        menu.date_time = datetime.now(timezone).strftime("%Y%m%d%H%M%S")

    vnp_TxnRef = menu.date_time + str(menu.machine_info["id"])

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
    requestData = prepare_data(0)
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

    print(url)

    return url


# def redirect_new_page(url):
#     webbrowser.open(url, new=1)


# Collect order information
# - ORDER CODER (PRIMARY KEY)
# - MACHINE ID
# - ITEMS (name, price per item, quantity, total cost per item)
# - TOTAL PRICE OF ORDER
# RETURN
# "<ORDER>": {
# 		"vending_machine_id" : "",
# 		"items": {
# 			"<item1>": {
# 				"price": <price>,
# 				"quantity": <quantity>,
# 				"cost": <cost>
# 			},
# 			"<item2>": {
# 				"price": <price>,
# 				"quantity": <quantity>,
# 				"cost": <cost>
# 			},
# 			...
# 		},
# 		"total_price": <total_price_of_order>,
# 	}
def collect_order_info():
    message = dict()

    # Retrieve sending URL to VN Pay

    # requestData["vnp_TxnRef"] is the ORDER Key
    globalRequestData = prepare_data(1)

    message[str(globalRequestData["vnp_TxnRef"])] = dict()

    # machine_info
    machine_info = menu.machine_info

    # menu.machine_info['id'] is the id of vending machine
    message[str(globalRequestData["vnp_TxnRef"])]["vending_machine_id"] = machine_info[
        "id"
    ]

    # Add items info
    message[str(globalRequestData["vnp_TxnRef"])]["items"] = dict()
    items = machine_info["items"]

    for item_name, item_properties in items.items():
        # st.write(item_properties["price"])
        message[str(globalRequestData["vnp_TxnRef"])]["items"][str(item_name)] = {
            "price": item_properties["price"],
            "quantity": item_properties["amount"],
            "cost": item_properties["price"] * item_properties["amount"],
        }

    # Add total cost
    message[str(globalRequestData["vnp_TxnRef"])][
        "total_price"
    ] = menu.calculate_total_price()

    message[str(globalRequestData["vnp_TxnRef"])]["transaction_status_code"] = ""
    return message


# Show pay button
def show_pay_button():
    st.warning("Please choose your payment method!")

    st.warning("If you want to cancel, please press CANCEL button below!")
    chosen_method = show_payment_method()

    if st.button("Pay"):
        if chosen_method == "VN Pay":
            url = create_order()

            open_page(url)
            time.sleep(5)
            switch_page("hidden_page")

        elif chosen_method == "Ngân Lượng Wallet":
            # status = create_order()
            st.write("Ngân lượng docx phức tạp quá!!!")

        elif chosen_method == "PayPal":
            st.write("Đang trong quá trình phát triển!")
        elif chosen_method == "Vui lòng chọn":
            st.write("Chọn đi thằng ml")


# Show cancel button
def show_cancel_button():
    if st.button("Cancel"):
        # Got bug that cannot extract machine id from url
        # switch_page("app")
        # Request user to scan QR code again to shop
        # End session
        st.write("Đang trong quá trình phát triển!")


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
