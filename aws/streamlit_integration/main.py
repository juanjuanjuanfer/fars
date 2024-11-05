import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="FARS",
    page_icon="📸",
    initial_sidebar_state="collapsed",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .subtitle {
        font-size: 20px;
        color: #666666;
        margin-bottom: 30px;
    }
    .team-header {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #333333;
    }
    .team-member {
        font-size: 16px;
        margin-left: 10px;
        color: #4F4F4F;
    }
    </style>
    """, unsafe_allow_html=True)

# Header Section
st.markdown('<p class="big-font">Facial Attendance Recognition System</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Welcome to FARS! Please login or register to continue.</p>', unsafe_allow_html=True)

# Authentication Section
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.write("")
    if st.button("Login", use_container_width=True):
        st.switch_page("pages/login.py")
    if st.button("Register", use_container_width=True):
        st.switch_page("pages/register.py")

# Separator
st.markdown("---")

# Team Credits Section
st.markdown('<p class="team-header" style="text-align: center;">Our Team</p>', unsafe_allow_html=True)

# Create three columns for team members
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<p class="team-header">Data Analysts</p>', unsafe_allow_html=True)
    st.markdown("""
    <p class="team-member">• Sonia Mendia</p>
    <p class="team-member">• Christopher Cumi</p>
    """, unsafe_allow_html=True)

with col2:
    st.markdown('<p class="team-header">Data Engineers</p>', unsafe_allow_html=True)
    st.markdown("""
    <p class="team-member">• Juan Fernandez</p>
    <p class="team-member">• Carlo Ek</p>
    """, unsafe_allow_html=True)

with col3:
    st.markdown('<p class="team-header">Data Scientists</p>', unsafe_allow_html=True)
    st.markdown("""
    <p class="team-member">• Miguel Bastarrachea</p>
    <p class="team-member">• Yahir Sulu</p>
    """, unsafe_allow_html=True)