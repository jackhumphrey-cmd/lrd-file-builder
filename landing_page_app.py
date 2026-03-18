import streamlit as st

st.set_page_config(
    page_title="LRD Migration Hub",
    page_icon="💳",
    layout="centered"
)

# --- Custom CSS Styling ---
st.markdown("""
<style>
/* Background */
body {
    background: linear-gradient(135deg, #0f172a, #1e293b);
}

/* Center container */
.main {
    text-align: center;
}

/* Title styling */
.title {
    font-size: 42px;
    font-weight: 700;
    color: white;
    margin-bottom: 10px;
}

/* Subtitle */
.subtitle {
    font-size: 18px;
    color: #cbd5f5;
    margin-bottom: 40px;
}

/* Card container */
.card-container {
    display: flex;
    justify-content: center;
    gap: 40px;
    margin-top: 30px;
}

/* Card */
.card {
    background: #111827;
    padding: 30px;
    border-radius: 16px;
    width: 280px;
    box-shadow: 0px 10px 25px rgba(0,0,0,0.4);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

/* Card hover */
.card:hover {
    transform: translateY(-8px);
    box-shadow: 0px 20px 40px rgba(0,0,0,0.6);
}

/* Card title */
.card-title {
    font-size: 20px;
    color: white;
    margin-bottom: 10px;
}

/* Card description */
.card-desc {
    font-size: 14px;
    color: #9ca3af;
    margin-bottom: 20px;
}

/* Buttons */
.button {
    display: inline-block;
    padding: 14px 24px;
    font-size: 16px;
    border-radius: 10px;
    text-decoration: none;
    color: white;
    transition: all 0.2s ease;
}

/* Stripe button */
.stripe {
    background: linear-gradient(135deg, #22c55e, #16a34a);
}

.stripe:hover {
    background: linear-gradient(135deg, #16a34a, #15803d);
}

/* Stax button */
.stax {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.stax:hover {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
}

/* Footer */
.footer {
    margin-top: 60px;
    font-size: 13px;
    color: #6b7280;
}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="title">💳 LRD Migration Hub</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Choose your migration workflow to get started</div>',
    unsafe_allow_html=True
)

# --- Cards ---
st.markdown("""
<div class="card-container">

    <!-- Stripe Card -->
    <div class="card">
        <div class="card-title">💳 Stripe / Authorize.net</div>
        <div class="card-desc">
            Use this workflow for direct token-based migrations with simple mapping.
        </div>
        <a href="https://stripe-lrd.streamlit.app" target="_blank" class="button stripe">
            Launch App →
        </a>
    </div>

    <!-- Stax Card -->
    <div class="card">
        <div class="card-title">🚀 Stax Migration</div>
        <div class="card-desc">
            Use this workflow for Stax migrations requiring token + mapping resolution.
        </div>
        <a href="https://lrd-stax.streamlit.app" target="_blank" class="button stax">
            Launch App →
        </a>
    </div>

</div>
""", unsafe_allow_html=True)

# --- Footer ---
st.markdown(
    '<div class="footer">Built for efficient recurring data migrations • LRD Tools</div>',
    unsafe_allow_html=True
)
