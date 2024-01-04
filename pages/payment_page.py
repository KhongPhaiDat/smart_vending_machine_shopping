import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import streamlit.components.v1 as components
import pages.menu as menu
import hashlib
import requests
import hmac
from datetime import datetime
import urllib.parse
from streamlit.components.v1 import html
import time

secret_key = "NRVNGGEOFCMRHZCLIRCUBYILIGPDRQKF"


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


# Create order and send to Ngan Luong.
def create_order():
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
    vnp_TxnRef = datetime.now().strftime("%Y%m%d%H%M%S") + str(menu.machine_info["id"])

    requestData = dict()
    requestData["vnp_Version"] = vnp_Version
    requestData["vnp_Command"] = vnp_Command
    requestData["vnp_TmnCode"] = vnp_TmnCode
    requestData["vnp_Amount"] = vnp_Amount
    requestData["vnp_CreateDate"] = datetime.now().strftime("%Y%m%d%H%M%S")
    requestData["vnp_CurrCode"] = vnp_CurrCode
    requestData["vnp_IpAddr"] = vnp_IpAddr
    requestData["vnp_Locale"] = vnp_Locale
    requestData["vnp_OrderInfo"] = vnp_OrderInfo
    requestData["vnp_OrderType"] = vnp_OrderType
    requestData["vnp_ReturnUrl"] = vnp_ReturnUrl
    requestData["vnp_TxnRef"] = vnp_TxnRef

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


# def redirect_new_page(url):
#     webbrowser.open(url, new=1)


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
        switch_page("app")


def main():
    show_total_price()
    show_pay_button()
    show_cancel_button()


if __name__ == "__main__":
    main()
