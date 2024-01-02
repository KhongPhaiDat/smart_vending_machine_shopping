import streamlit as st

# Get machine info base on ID
machine_info = dict()

# Get item new quantity
item_new_quantity = dict()

# Just for testing to display
machine_info = {
    "ID": "123456",
    "items": {
        "milk": {"amount": 7, "price": 10},
        "coke": {"amount": 9, "price": 10},
        "water": {"amount": 20, "price": 10},
        "doll": {"amount": 10, "price": 10},
        "pencil": {"amount": 10, "price": 10},
    },
}


# Main structure of menu page
def main():
    st.title("Smart Vending Shopping")

    for item in machine_info["items"].keys():
        item_new_quantity[item] = machine_info["items"][item]["amount"]

    # User input new quantity
    insert_amount_item()

    # User can view total price
    show_total_price()


# Show info of item
def show_items(name_item, info_item):
    # Show name
    st.write(name_item)

    # Show amount of item
    amount = info_item["amount"]
    st.write("Quantity remaining: ", amount)

    # Show price of item
    price = info_item["price"]
    st.write("Price: ", price)


# User input quantity of item
def get_new_quantity(name_item):
    new_quantity = st.number_input(
        "Input your quantity: ",
        key=name_item,
        min_value=0,
        max_value=machine_info["items"][name_item]["amount"],
        step=1,
    )
    return new_quantity


# User can input amount to buy
def insert_amount_item():
    st.write("Here is the menu of vending machine")

    items = machine_info["items"]

    for item, info_item in items.items():
        show_items(item, info_item)
        item_new_quantity[item] = get_new_quantity(item)


# Show total price of shopping
def show_total_price():
    total_price = 0

    for item, new_quantity in item_new_quantity.items():
        total_price = total_price + int(new_quantity) * int(
            machine_info["items"][item]["price"]
        )

    st.write("Total Price: ", total_price)


if __name__ == "__main__":
    main()
