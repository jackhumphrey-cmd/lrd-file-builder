import streamlit as st

st.set_page_config(
    page_title="LRD Migration Hub",
    page_icon="💳",
    layout="centered"
)

# -----------------------------
# Header
# -----------------------------
st.markdown(
    "<h1 style='text-align: center;'>LRD Migration Hub</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align: center; color: gray;'>Choose your migration workflow to get started</p>",
    unsafe_allow_html=True
)

st.markdown("---")

# -----------------------------
# Buttons Layout
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Stripe / Authorize.net")
    st.caption("Direct token-based migrations with simple mapping.")
    st.link_button(
        "Launch App →",
        "https://stripe-lrd.streamlit.app",
        use_container_width=True
    )

with col2:
    st.markdown("### Stax Migration")
    st.caption("Token + mapping-based migration with intelligent matching.")
    st.link_button(
        "Launch App →",
        "https://lrd-stax.streamlit.app",
        use_container_width=True
    )

st.markdown("---")

# -----------------------------
# Footer
# -----------------------------
st.markdown(
    "<p style='text-align: center; font-size: 12px; color: gray;'>Built for efficient recurring data migrations • LRD Tools</p>",
    unsafe_allow_html=True
)
