import streamlit as st
from streamlit_extras.switch_page_button import switch_page


def main():
    # Cancel cart and navigate to menu
    cancel_cart()

    # Confirm cart and go to payment page
    payment_cart()


def cancel_cart():
    if st.button("CANCEL"):
        switch_page("app")


def payment_cart():
    if st.button("CONFIRM"):
        switch_page("payment_page")


if __name__ == "__main__":
    main()
