import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pages.menu as menu


# Show total price
def show_total_price():
    st.write("Total Price: ", menu.calculate_total_price())


payment_methods = ["Vui lòng chọn", "Ngân Lượng Wallet", "PayPal"]


# Show payment method
def show_payment_method():
    chosen_method = st.selectbox("Choose a payment method: ", payment_methods)
    return chosen_method


# Show pay button
def show_pay_button():
    st.warning("Please choose your payment method!")

    st.warning("If you want to cancel, please press CANCEL button below!")
    chosen_method = show_payment_method()

    if st.button("Pay"):
        if chosen_method == "Ngân Lượng Wallet":
            switch_page("checkout")
        elif chosen_method == "PayPal":
            switch_page("checkout")
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
