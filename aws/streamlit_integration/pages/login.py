import streamlit as st
import utils
import sys
import os

# Add the parent directory to sys.path if utils.py is in the parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Initialize session state for login status if it doesn't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Page configuration
st.set_page_config(
    page_title="FARS Login",
    page_icon="🔐",
    layout="centered"
)

# Custom CSS for enhanced styling
st.markdown("""
    <style>
    /* General background */
    body {
        background-color: #f0f2f6;
    }
    /* Login container */
    .login-container {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        max-width: 400px;
        margin: auto;
    }
    /* Main title */
    .main-title {
        font-size: 2.5rem;
        color: #003366;
        text-align: center;
        margin-bottom: 20px;
        font-weight: bold;
    }
    /* Subtitle */
    .subtitle {
        font-size: 1rem;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 30px;
    }
    /* Input fields */
    .stTextInput>div>div>input {
        border-radius: 5px;
        padding: 10px;
        border: 1px solid #ccc;
    }
    /* Login button */
    .stButton>button {
        background-color: #003366;
        color: white;
        border: none;
        padding: 12px 24px;
        font-size: 16px;
        border-radius: 8px;
        cursor: pointer;
        transition: background-color 0.3s;
        width: 100%;
        margin-top: 10px;
    }
    .stButton>button:hover {
        background-color: #357ABD;
    }
    /* Error and success messages */
    .stAlert {
        border-radius: 5px;
        padding: 10px;
    }
    /* Centered images */
    .image-center {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 50%;
    }
    </style>
    """, unsafe_allow_html=True)

# Login form container
with st.container():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">FARS Login</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Enter your credentials to access the system</p>', unsafe_allow_html=True)

    # Display the login form if not logged in
    if not st.session_state.logged_in:
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        if st.button("Login"):
            if utils.verify_login(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login Successful")
                st.image("https://media.tenor.com/YtCPsB3gZu8AAAAi/mymelody-my.gif", use_column_width=True)
                # Automatically redirect after successful login
                st.experimental_rerun()
                st.experimental_set_query_params(page="courses")
            else:
                st.error("Invalid credentials. Please check your username and password.")
                st.image("https://media1.tenor.com/m/7Rw8rOLsNOEAAAAC/moodeng.gif", use_column_width=True)
    else:
        # If already logged in, show a success message and redirect
        st.success(f"Already logged in as {st.session_state.username}. Redirecting...")
        st.image("https://media.tenor.com/YtCPsB3gZu8AAAAi/mymelody-my.gif", use_column_width=True)
        st.experimental_rerun()
        st.experimental_set_query_params(page="courses")

    st.markdown('</div>', unsafe_allow_html=True)
