import streamlit as st


def create_streamlit_page():
    # Use columns to layout the elements similar to the image provided
    col1, col2 = st.columns([1, 2])  # Adjust the ratio based on your layout needs

    with col1:
        st.image("images/chocolate.jpg")

        # Placeholder for the image or chart
        # st.image("path_to_your_image_here.png")  # Replace with your local image path

    with col2:
        st.write("Item name: Chocolate")
        st.write("Price: 200")
        st.write("Quantity remaining: 20")
        # Assuming the circles are for quantity selection
        quantity = st.number_input(
            "Input your quantity: ",
            key="abc",
            min_value=0,
            max_value=20,
            step=1,
        )


if __name__ == "__main__":
    create_streamlit_page()
