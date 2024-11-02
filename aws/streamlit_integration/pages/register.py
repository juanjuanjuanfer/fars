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
    page_title="FARS Registration",
    page_icon="📝",
    layout="centered"
)

# Custom CSS for enhanced styling
st.markdown("""
    <style>
    /* General background */
    body {
        background-color: #f0f2f6;
    }
    /* Registration container */
    .register-container {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        max-width: 500px;
        margin: auto;
    }
    /* Main title */
    .main-title {
        font-size: 2.5rem;
        color: #003366; /* Same blue as login */
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
    /* Register button */
    .stButton>button {
        background-color: #003366; /* Same blue as login */
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
        background-color: #357ABD; /* Darker blue on hover */
    }
    /* Secondary button (Go to Courses) */
    .stButton.secondary>button {
        background-color: #2980b9; /* Slightly different blue for secondary action */
    }
    .stButton.secondary>button:hover {
        background-color: #1c5980;
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

# Registration form container
with st.container():
    st.markdown('<div class="register-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">FARS Registration</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Please enter your information to register</p>', unsafe_allow_html=True)

    # If the user is already logged in, show a message and redirect button
    if st.session_state.logged_in:
        st.success(f"You are already logged in as **{st.session_state.username}**.")
        if st.button("Go to Courses", key="goto_courses", css_class="secondary"):
            st.switch_page("pages/courses.py")
    else:
        # Registration form
        name = st.text_input("Name", placeholder="Enter your full name")
        username = st.text_input("Username", placeholder="Choose a username")
        password = st.text_input("Password", type="password", placeholder="Create a password")
        email = st.text_input("Email", placeholder="Enter your email address")

        if st.button("Register"):
            if utils.verify_register(email):
                registration_success, registration_error = utils.register_user(name, username, password, email)
                if registration_success:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Registration Successful!")
                    st.image("https://media.tenor.com/YtCPsB3gZu8AAAAi/mymelody-my.gif", use_column_width=True)
                    # Automatically redirect after successful registration
                    st.experimental_rerun()
                    st.switch_page("pages/courses.py")
                else:
                    st.error("Registration Failed. Please try again.")
                    st.write("Possible reasons: Username already exists or server error.")
                    st.image("https://media1.tenor.com/m/FafJhrYbdZQAAAAd/sailor-moon-bishoujo-senshi-sailor-moon.gif", use_column_width=True)
            else:
                st.warning("Email is already in use. Please use a different email address.")
                st.image("https://media1.tenor.com/m/FafJhrYbdZQAAAAd/sailor-moon-bishoujo-senshi-sailor-moon.gif", use_column_width=True)

    st.markdown('</div>', unsafe_allow_html=True)
