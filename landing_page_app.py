# lrd_landing_page.py

import streamlit as st

st.set_page_config(
    page_title="💳 LRD Migration Landing Page",
    page_icon="💳",
    layout="wide"
)

st.title("💳 LRD Migration Landing Page")
st.markdown(
    """
    Welcome! Select which migration workflow you want to run:
    """
)

st.markdown("---")

# Create two columns for buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Stripe / Authorize.net Migration", key="stripe"):
        st.markdown(
            "[Open Stripe / Authorize.net App](https://stripe-lrd.streamlit.app)"
        )

with col2:
    if st.button("🚀 Stax Migration", key="stax"):
        st.markdown(
            "[Open Stax App](https://lrd-stax.streamlit.app)"
        )

st.info(
    "Click the button above to open the selected app in a new tab. "
    "Each workflow runs independently with its required files."
)
