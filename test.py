from datetime import datetime
import hashlib
import hmac
import requests
import urllib.parse

secret_key = "NRVNGGEOFCMRHZCLIRCUBYILIGPDRQKF"


def hmacsha512(key, data):
    byteKey = key.encode("utf-8")
    byteData = data.encode("utf-8")
    return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()


def create_order():
    vnp_Version = "2.1.0"
    vnp_Command = "pay"
    vnp_TmnCode = "SMXX9OJQ"
    vnp_Amount = "1000"
    # vnp_BankCode = ""
    vnp_CreateDate = "20240104095959"
    vnp_CurrCode = "VND"
    vnp_IpAddr = "113.161.0.216"
    vnp_Locale = "vn"
    vnp_OrderInfo = "Thanh toán đơn hàng với giá trị 1000"
    vnp_OrderType = "other"
    vnp_ReturnUrl = "https://smartvendingmachine.shop/return"
    vnp_TxnRef = "23554"

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
    print(url)


create_order()
