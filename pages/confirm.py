import streamlit as st
from streamlit_extras.switch_page_button import switch_page


def main():
    cancel_cart()


def cancel_cart():
    if st.button("CANCEL"):
        switch_page("app")


if __name__ == "__main__":
    main()
