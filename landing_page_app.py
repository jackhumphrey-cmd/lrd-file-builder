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

/* Background */
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

/* Card link wrapper */
.card-link {
    text-decoration: none;
}

/* Card */
.card {
    background: #ffffff;
    padding: 24px;
    border-radius: 14px;
    border: 1px solid #e0e6ef;
    transition: all 0.25s ease;
    height: 100%;
    cursor: pointer;
}

/* Hover inversion */
.card:hover {
    background: #111111;
    color: #ffffff;
    transform: translateY(-6px);
    box-shadow: 0 12px 28px rgba(0,0,0,0.15);
}

/* Text inversion */
.card:hover h3,
.card:hover p,
.card:hover span {
    color: #ffffff !important;
}

/* Footer */
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
# Cards (Clickable)
# -----------------------------
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <a class="card-link" href="https://stripe-lrd.streamlit.app" target="_self">
        <div class="card">
            <h3>Stripe / Authorize.net Migrations</h3>
            <p>Direct token-based migrations with simple mapping.</p>
        </div>
    </a>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <a class="card-link" href="https://lrd-stax.streamlit.app" target="_self">
        <div class="card">
            <h3>Stax Migrations</h3>
            <p>Token + mapping-based migration with intelligent matching.</p>
        </div>
    </a>
    """, unsafe_allow_html=True)

# -----------------------------
# Footer
# -----------------------------
st.markdown(
    "<div class='footer'>Built for efficient recurring data migrations • LRD Tools</div>",
    unsafe_allow_html=True
)
