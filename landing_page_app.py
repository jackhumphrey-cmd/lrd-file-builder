import streamlit as st

st.set_page_config(
    page_title="LRD Migration Hub",
    page_icon="💳",
    layout="centered"
)

# -----------------------------
# CSS
# -----------------------------
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #f7f9fc 0%, #e6ecf5 100%);
    color: #111111;
}

.block-container {
    max-width: 800px;
    padding-top: 2rem;
}

.title {
    text-align: center;
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 0;
}

.subtitle {
    text-align: center;
    color: #555;
    margin-bottom: 2rem;
}

.card {
    background: #ffffff;
    padding: 25px;
    border-radius: 16px;
    border: 1px solid #e0e6ef;
    transition: all 0.25s ease;
    height: 100%;
}

.card:hover {
    background: #111111;
    color: #ffffff;
    transform: translateY(-6px);
    box-shadow: 0 12px 30px rgba(0,0,0,0.15);
}

.card:hover h3,
.card:hover p,
.card:hover span {
    color: #ffffff !important;
}

/* Style Streamlit buttons */
.stButton > button {
    width: 100%;
    border-radius: 10px;
    background-color: #111111;
    color: #ffffff;
    border: 1px solid #111111;
    transition: all 0.25s ease;
}

/* Button hover inversion */
.stButton > button:hover {
    background-color: #ffffff;
    color: #111111;
    border: 1px solid #111111;
}

.footer {
    text-align: center;
    font-size: 12px;
    color: #666;
    margin-top: 3rem;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# Header
# -----------------------------
st.markdown("<div class='title'>💳 LRD Migration Hub</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Choose your migration workflow to get started</div>", unsafe_allow_html=True)

# -----------------------------
# Cards Layout
# -----------------------------
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Stripe / Authorize.net")
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
