import streamlit as st
import pages.payment_page as payment_page


# Add order to database
def add_orders_to_database():
    vnp_ResponseCode = st.experimental_get_query_params()["vnp_ResponseCode"][0]

    order_message = payment_page.collect_order_info()

    key = ""
    for a, _ in order_message.items():
        if key == "":
            key = a
            break

    order_message[key]["transaction_status_code"] = vnp_ResponseCode
    #
    #
    return order_message


st.write(add_orders_to_database())
