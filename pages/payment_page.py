import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pages.menu as menu

# Show total price
st.write("Total Price: ", menu.calculate_total_price())

# Show payment method
st.write("Please choose your payment method!")
