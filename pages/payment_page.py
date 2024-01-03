import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pages.menu as menu


# Show total price
def show_total_price():
    st.write("Total Price: ", menu.calculate_total_price())


payment_methods = ["Ngân Lượng Wallet", "Pay Pal"]


# Show payment method
def show_payment_methods():
    st.write("Please choose your payment method!")

    chosen_method = [0 for _ in range(len(payment_methods))]

    for i in range(len(payment_methods)):
        chosen_method[i] = st.button(payment_methods[i])

    if sum(chosen_method) == 1:
        for i in range(len(payment_methods)):
            if chosen_method[i]:
                st.session_state[payment_methods[i]] = True
                return payment_methods[i]

    return None


# Show pay button
def show_pay_button():
    chosen_method = None
    chosen_method = show_payment_methods()

    if chosen_method != None and st.session_state[chosen_method] == True:
        st.warning(f"You choose to pay via {chosen_method}")
        if st.button("Pay"):
            st.write("Haha")


def main():
    show_total_price()
    # show_payment_methods()
    show_pay_button()


if __name__ == "__main__":
    main()
