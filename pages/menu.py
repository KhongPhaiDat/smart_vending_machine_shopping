import streamlit as st
import modules.menu_component as menu_component
from streamlit_extras.switch_page_button import switch_page


# Main structure of menu page
def main():
    st.title("Smart Vending Machine Shopping")
    for item in machine_info["items"].keys():
        item_new_quantity[item] = machine_info["items"][item]["amount"]
    # User input new quantity
    insert_amount_item()
    # User can view total price
    show_total_price()
    # User confirm cart
    confirm()


# Show info of item
def show_items(name_item, info_item):
    col1, col2 = st.columns([1, 2])
    with col1:
        try:
            st.image(f"images/{name_item}.jpg", use_column_width=True)
        except:
            st.image("images/unknown.jpg", use_column_width=True)
    with col2:
        st.write(f"Price: {info_item['price']}")
        st.write(f"Quantity remaining: {info_item['amount']}")
        # Assuming the circles are for quantity selection
        quantity = get_new_quantity(name_item)
        item_new_quantity[name_item] = quantity
    st.markdown("<hr/>", unsafe_allow_html=True)


# User input quantity of item
def get_new_quantity(name_item):
    new_quantity = st.number_input(
        "Input your quantity: ",
        key=name_item,
        min_value=0,
        max_value=int(machine_info["items"][name_item]["amount"]),
        step=1,
    )
    return new_quantity


# User can input amount to buy
def insert_amount_item():
    st.write("Here is the menu of vending machine")
    items = machine_info["items"]
    for item, info_item in items.items():
        show_items(item, info_item)


# Calculate total price
def calculate_total_price():
    total_price = 0
    for item, new_quantity in item_new_quantity.items():
        total_price = total_price + int(new_quantity) * int(
            machine_info["items"][item]["price"]
        )
    return total_price


# Show total price of shopping
def show_total_price():
    total_price = calculate_total_price()
    st.write("Total Price: ", total_price)


# Go to payment page
def confirm():
    if st.button("Go to Purchase"):
        total_price = calculate_total_price()
        if total_price == 0:
            st.warning("Vui lòng hãy chọn mặt hàng để thanh toán!")
        else:
            switch_page("payment_page")


# Initialize date time
date_time = ""

# Init menu component
menu_component = menu_component.MenuComponent()
id = st.query_params["id"]

# Get machine info base on ID
machine_info = menu_component.returnMenuByMachineID(id=id)

# Get item new quantity
item_new_quantity = dict()
