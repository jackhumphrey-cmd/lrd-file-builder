import streamlit as st

st.set_page_config(
    page_title="LRD Migration Landing Page",
    page_icon="💳",
    layout="centered"
)

st.title("💳 LRD Migration Builder")
st.markdown(
    "Choose which migration tool to use. Click a button below to launch the corresponding app."
)

# --- Button row with spacing ---
buttons_html = """
<div style="text-align:center; margin-top:50px; margin-bottom:60px;">
    <a href="https://stripe-lrd.streamlit.app" target="_blank" style="margin-right:40px;">
        <button style="
            background-color:#4CAF50;
            color:white;
            padding:20px 40px;
            font-size:20px;
            border:none;
            border-radius:10px;
            cursor:pointer;
        ">
            Stripe/Authorize.net Migration
        </button>
    </a>
    <a href="https://lrd-stax.streamlit.app" target="_blank">
        <button style="
            background-color:#2196F3;
            color:white;
            padding:20px 40px;
            font-size:20px;
            border:none;
            border-radius:10px;
            cursor:pointer;
        ">
            Stax Migration
        </button>
    </a>
</div>
"""

st.markdown(buttons_html, unsafe_allow_html=True)
