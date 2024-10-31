import streamlit as st
import utils

# Initialize session state for login status if it doesn't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

st.title("FARS Login")

# Only show login form if not logged in
if not st.session_state.logged_in:
    st.write("Please enter your username and password")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if utils.verify_login(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login Successful")
            st.image("https://media.tenor.com/YtCPsB3gZu8AAAAi/mymelody-my.gif")
            # Automatically redirect after successful login
            st.switch_page("pages/courses.py")  # Update this path as needed
        else:
            st.error("Who tf are you?")
            st.image("https://media1.tenor.com/m/7Rw8rOLsNOEAAAAC/moodeng.gif")
else:
    # If already logged in, just show the redirect button
    st.success(f"Already logged in as {st.session_state.username}")
    st.switch_page("pages/courses.py")  # Update this path as needed