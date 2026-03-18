# lrd_landing_page.py

import streamlit as st

st.set_page_config(
    page_title="💳 LRD Migration Landing Page",
    page_icon="💳",
    layout="wide"
)

st.title("💳 LRD Migration Landing Page")
st.markdown(
    "Welcome! Select which migration workflow you want to run:"
)
st.markdown("---")

# HTML buttons that open apps in new tabs
stripe_button = """
<div style="text-align:center">
    <a href="https://stripe-lrd.streamlit.app" target="_blank">
        <button style="
            background-color:#4CAF50;
            color:white;
            padding:20px 40px;
            font-size:20px;
            border:none;
            border-radius:10px;
            cursor:pointer;
            margin-right:20px;
        ">
            🚀 Stripe / Authorize.net Migration
        </button>
    </a>
</div>
"""

stax_button = """
<div style="text-align:center; margin-top:20px;">
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
            🚀 Stax Migration
        </button>
    </a>
</div>
"""

st.markdown(stripe_button, unsafe_allow_html=True)
st.markdown(stax_button, unsafe_allow_html=True)

st.info(
    "Click a button to open the selected app in a new tab. "
    "Each workflow runs independently with its required files."
)
