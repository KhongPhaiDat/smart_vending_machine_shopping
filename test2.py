import streamlit as st
from streamlit.components.v1 import html


# Function to create a button that runs JavaScript to close the current tab
def close_tab_button():
    button_html = """
        <html>
            <body>
                <button onclick="window.close();">Close Tab</button>
            </body>
        </html>
        """
    html(button_html)


# Display the button in Streamlit app
close_tab_button()
