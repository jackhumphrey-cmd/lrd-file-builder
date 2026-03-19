import streamlit as st

st.set_page_config(
    page_title="LRD Migration Hub",
    page_icon="💳",
    layout="centered"
)

# -----------------------------
# Header
# -----------------------------
st.title("💳 LRD Migration Hub")
st.subheader("Choose your migration workflow to get started")

st.write("")

# -----------------------------
# Stripe Card
# -----------------------------
with st.container(border=True):
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("### Stripe / Authorize.net Migrations")
        st.write("Direct token-based migrations with simple mapping.")

    with col2:
        st.write("")
        st.write("")
        st.link_button(
            "Launch →",
            "https://stripe-lrd.streamlit.app",
            use_container_width=True
        )

st.write("")

# -----------------------------
# Stax Card
# -----------------------------
with st.container(border=True):
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("### Stax Migrations")
        st.write("Token + mapping-based migration with intelligent matching.")

    with col2:
        st.write("")
        st.write("")
        st.link_button(
            "Launch →",
            "https://lrd-stax.streamlit.app",
            use_container_width=True
        )

st.write("")

# -----------------------------
# Footer
# -----------------------------
st.divider()
st.caption("Built for efficient recurring data migrations • LRD Tools")
