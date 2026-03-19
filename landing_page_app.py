import streamlit as st

st.set_page_config(
    page_title="LRD Migration Hub",
    page_icon="💳",
    layout="centered"
)

# -----------------------------
# CSS (hover inversion)
# -----------------------------
st.markdown("""
<style>

/* Page background */
.stApp {
    background: #f7f9fc;
}

/* Header */
.title {
    text-align: center;
    font-size: 40px;
    font-weight: 700;
}

.subtitle {
    text-align: center;
    color: #666;
    margin-bottom: 2rem;
}

/* Card styling via column containers */
.card {
    background: #ffffff;
    padding: 24px;
    border-radius: 14px;
    border: 1px solid #e0e6ef;
    transition: all 0.25s ease;
    height: 100%;
}

/* Hover inversion */
.card:hover {
    background: #111111;
    color: #ffffff;
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.12);
}

/* Ensure text flips */
.card:hover p,
.card:hover h3,
.card:hover span {
    color: #ffffff !important;
}

/* Buttons */
.stLinkButton > a {
    background-color: #111111;
    color: #ffffff !important;
    border-radius: 10px;
    padding: 10px 16px;
    text-align: center;
    display: inline-block;
    width: 100%;
    border: 1px solid #111111;
    transition: all 0.25s ease;
}

/* Button hover inversion */
.stLinkButton > a:hover {
    background-color: #ffffff;
    color: #111111 !important;
    border: 1px solid #111111;
}

.footer {
    text-align: center;
    font-size: 12px;
    color: #777;
    margin-top: 2.5rem;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# Header
# -----------------------------
st.markdown("<div class='title'>💳 LRD Migration Hub</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Choose your migration workflow to get started</div>", unsafe_allow_html=True)

# -----------------------------
# Columns (cards)
# -----------------------------
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Stripe / Authorize.net Migrations")
    st.caption("Direct token-based migrations with simple mapping.")
    st.link_button(
        "Launch App →",
        "https://stripe-lrd.streamlit.app",
        use_container_width=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Stax Migrations")
    st.caption("Token + mapping-based migration with intelligent matching.")
    st.link_button(
        "Launch App →",
        "https://lrd-stax.streamlit.app",
        use_container_width=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Footer
# -----------------------------
st.markdown(
    "<div class='footer'>Built for efficient recurring data migrations • LRD Tools</div>",
    unsafe_allow_html=True
)
