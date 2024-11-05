import streamlit as st
import utils


if not 'logged_in' in st.session_state:
    st.session_state.logged_in = False

# if already loged in show button to redirect to courses
if st.session_state.logged_in:
    st.write("You are already logged in")
    if st.button("Go to Courses"):
        st.switch_page("pages/courses.py")

st.title("FARS Register")

st.write("Please enter your information to register")
name = st.text_input("Name")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
email = st.text_input("Email")

if st.button("Register"):
    if utils.verify_register(email):

        if utils.register_user(name,username,password,email):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Registration Successful")
            st.image("https://media.tenor.com/YtCPsB3gZu8AAAAi/mymelody-my.gif")

        else:
            st.write("Registration Failed")
            st.write("Please try again, maybe user arleady exists we don't know jejw")
            st.image("https://media1.tenor.com/m/FafJhrYbdZQAAAAd/sailor-moon-bishoujo-senshi-sailor-moon.gif")
    else:
        st.warning("Email already in use.")
