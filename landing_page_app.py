import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(
    page_title="LRD Migration Hub",
    page_icon="💳",
    layout="centered"
)

# -----------------------------
# Sidebar Navigation
# -----------------------------
with st.sidebar:
    selected = option_menu(
        menu_title="LRD Migration Hub",
        options=["Home", "Stripe / Authorize.net", "Stax Migrations"],
        icons=["house", "credit-card", "layers"],
        default_index=0
    )

# -----------------------------
# Home Page (Landing)
# -----------------------------
if selected == "Home":
    st.title("💳 LRD Migration Hub")
    st.subheader("Choose your migration workflow")

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        st.container(border=True)
        st.markdown("### Stripe / Authorize.net")
        st.write("Direct token-based migrations with simple mapping.")
        st.page_link("https://stripe-lrd.streamlit.app", label="Launch External App →")

    with col2:
        st.container(border=True)
        st.markdown("### Stax Migrations")
        st.write("Token + mapping-based migration with intelligent matching.")
        st.page_link("https://lrd-stax.streamlit.app", label="Launch External App →")

# -----------------------------
# Stripe Tool Page
# -----------------------------
elif selected == "Stripe / Authorize.net":
    st.title("💳 Stripe / Authorize.net Migrations")

    st.write("This section will contain your Stripe migration tool UI.")

    st.info("You can either embed your logic here or redirect to your existing app.")

    st.link_button(
        "Open Full Tool →",
        "https://stripe-lrd.streamlit.app"
    )

# -----------------------------
# Stax Tool Page
# -----------------------------
elif selected == "Stax Migrations":
    st.title("🏦 Stax Migrations")

    st.write("This section will contain your Stax migration tool UI.")

    st.info("You can either embed your logic here or redirect to your existing app.")

    st.link_button(
        "Open Full Tool →",
        "https://lrd-stax.streamlit.app"
    )
