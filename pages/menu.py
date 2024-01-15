import streamlit as st
import modules.menu_component as menu_component
from streamlit_extras.switch_page_button import switch_page


# Main structure of menu page
def main():
    id = st.query_params["id"]

    # Get machine info base on ID
    machine_info = menu_component.returnMenuByMachineID(id=id)
    if "machine_info" not in st.session_state:
        st.session_state["machine_info"] = machine_info

    # Get item new quantity
    item_new_quantity = dict()

    st.title("Smart Vending Machine Shopping")
    for item in machine_info["items"].keys():
        item_new_quantity[item] = machine_info["items"][item]["amount"]
    # User input new quantity
    insert_amount_item(machine_info, item_new_quantity)
    # User can view total price
    show_total_price(machine_info, item_new_quantity)
    # User confirm cart
    confirm(machine_info, item_new_quantity)


# Show info of item
def show_items(name_item, info_item, item_new_quantity, machine_info):
    col1, col2 = st.columns([1, 2])
    with col1:
        try:
            st.image(f"static/{name_item}.jpg", width=150, use_column_width=False)
        except:
            st.image("static/unknown.jpg", width=150, use_column_width=False)
    with col2:
        st.write(f"Price: {info_item['price']}")
        st.write(f"Quantity remaining: {info_item['amount']}")
        # Assuming the circles are for quantity selection
        quantity = get_new_quantity(name_item, machine_info)
        item_new_quantity[name_item] = quantity
    st.markdown("<hr/>", unsafe_allow_html=True)


# User input quantity of item
def get_new_quantity(name_item, machine_info):
    new_quantity = st.number_input(
        "Input your quantity: ",
        key=name_item,
        min_value=0,
        max_value=int(machine_info["items"][name_item]["amount"]),
        step=1,
    )
    return new_quantity


# User can input amount to buy
def insert_amount_item(machine_info, item_new_quantity):
    items = machine_info["items"]
    for item, info_item in items.items():
        show_items(item, info_item, item_new_quantity, machine_info)


# Calculate total price
def calculate_total_price(machine_info, item_new_quantity):
    total_price = 0
    for item, new_quantity in item_new_quantity.items():
        total_price = total_price + int(new_quantity) * int(
            machine_info["items"][item]["price"]
        )
    return total_price


# Show total price of shopping
def show_total_price(machine_info, item_new_quantity):
    total_price = calculate_total_price(machine_info, item_new_quantity)
    custom_text = f"Total Price: {total_price}"
    st.markdown(
        f'<p style="font-size: 24px;">{custom_text}</p>', unsafe_allow_html=True
    )


# Go to payment page
def confirm(machine_info, item_new_quantity):
    if st.button("Go to Purchase"):
        total_price = calculate_total_price(machine_info, item_new_quantity)
        if total_price == 0:
            st.warning("Vui lòng hãy chọn mặt hàng để thanh toán!")
        else:
            if "item_new_quantity" not in st.session_state:
                st.session_state["item_new_quantity"] = item_new_quantity
            switch_page("payment_page")


# Initialize date time
date_time = ""

# Init menu component
menu_component = menu_component.MenuComponent()
