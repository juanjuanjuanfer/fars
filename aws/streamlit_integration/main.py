import streamlit as st
import base64

# Set page configuration
st.set_page_config(
    page_title="FARS - Facial Attendance Recognition System",
    page_icon=":camera:",
    layout="wide"
)

# Custom CSS for enhanced styling
st.markdown("""
    <style>
    .main-title {
        font-size: 3rem;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 30px;
        font-weight: bold;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #34495E;
        text-align: center;
        margin-bottom: 40px;
    }
    .stButton>button {
        background-color: #3498DB;
        color: white;
        border: none;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 10px 2px;
        transition-duration: 0.4s;
        cursor: pointer;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background-color: #2980B9;
    }
    .credits-section {
        background-color: #F7F9FB;
        padding: 20px;
        border-radius: 10px;
        margin-top: 30px;
    }
    .credits-title {
        font-size: 1.5rem;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 20px;
        font-weight: bold;
    }
    .team-section {
        text-align: center;
        color: #34495E;
    }
    </style>
    """, unsafe_allow_html=True)

# Main content
st.markdown('<h1 class="main-title">FARS</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Facial Attendance Recognition System</p>', unsafe_allow_html=True)

# Center the buttons
col1, col2, col3 = st.columns(3)
with col2:
    login_col, register_col = st.columns(2)
    with login_col:
        if st.button("Login", key="login_btn"):
            st.switch_page("pages/login.py")
    with register_col:
        if st.button("Register", key="register_btn"):
            st.switch_page("pages/register.py")

# Credits section
st.markdown('<div class="credits-section">', unsafe_allow_html=True)
st.markdown('<h2 class="credits-title">Our Team</h2>', unsafe_allow_html=True)

# Team members
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="team-section"><h3>Data Analysts</h3>', unsafe_allow_html=True)
    st.write("• Sonia Mendia")
    st.write("• Christopher Cumi")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="team-section"><h3>Data Engineers</h3>', unsafe_allow_html=True)
    st.write("• Juan Fernandez")
    st.write("• Carlo Ek")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="team-section"><h3>Data Engineers</h3>', unsafe_allow_html=True)
    st.write("• Miguel Bastarrachea")
    st.write("• Yahir Sulu")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)