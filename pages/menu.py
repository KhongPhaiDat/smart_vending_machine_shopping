import streamlit as st

# Get machine info base on ID
machine_info = dict()

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

    insert_amount_item()


# Show info of item
def show_items(name_item, info_item):
    st.write("Provide information about item")


def get_new_quantity(name_item):
    new_quantity = st.number_input(
        "Input your quantity: ", key=name_item, min_value=0, step=1
    )


# User can input amount to buy
def insert_amount_item():
    st.write("Here is the menu of vending machine")

    items = machine_info["items"]

    num_items = len(items.keys())
    item_new_quantity = dict()

    for item, info_item in items.items():
        show_items(item, info_item)
        item_new_quantity[item] = get_new_quantity(item)


if __name__ == "__main__":
    main()
