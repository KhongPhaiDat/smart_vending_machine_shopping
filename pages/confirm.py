import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pages.menu as menu
import pandas as pd


def main():
    # Show items info in cart
    show_item_info()

    # Cancel cart and navigate to menu
    cancel_cart()

    # Confirm cart and go to payment page
    payment_cart()


def show_item_info():
    st.write("Review Your Cart")

    data = dict()
    data["Item"] = list()
    data["Quantity"] = list()
    data["Price Per Item"] = list()

    show_items = menu.item_new_quantity
    machine_info = menu.machine_info

    for item, amount in show_items.items():
        data["Item"].append(str(item))
        data["Quantity"].append(str(amount))
        data["Price Per Item"].append(str(machine_info["items"][item]["price"]))

    df = pd.DataFrame(data)
    st.write(df)
    st.write("Total Price: ", menu.calculate_total_price())


def cancel_cart():
    if st.button("CANCEL"):
        switch_page("app")


def payment_cart():
    if st.button("CONFIRM"):
        switch_page("payment_page")


if __name__ == "__main__":
    main()
