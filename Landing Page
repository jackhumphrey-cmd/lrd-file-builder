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
    - **Stripe / Authorize.net**
    - **Stax**
    """
)

# Option to select workflow
workflow = st.radio(
    "Select Migration Workflow:",
    ("Stripe / Authorize.net", "Stax")
)

st.markdown("---")

# Provide a button to open the selected app
if workflow == "Stripe / Authorize.net":
    st.markdown(
        "[🚀 Launch Stripe / Authorize.net Migration](https://stripe-lrd.streamlit.app)"
    )
elif workflow == "Stax":
    st.markdown(
        "[🚀 Launch Stax Migration](https://lrd-stax.streamlit.app)"
    )

st.info(
    "Click the link above to open the selected app. "
    "Each workflow runs independently with its required files."
)
