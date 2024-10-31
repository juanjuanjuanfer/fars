import streamlit as st
import utils


st.title("FARS Register")

st.write("Please enter your information to register")
name = st.text_input("Name")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
email = st.text_input("Email")

if st.button("Register"):
    if utils.register_user(name,username,password,email):
        st.success("Registration Successful")
        st.image("https://media.tenor.com/YtCPsB3gZu8AAAAi/mymelody-my.gif")
        if st.button("Go to Login"):
            st.switch_page("pages/login.py")
    else:
        st.write("Registration Failed")
        st.write("Please try again, maybe user arleady exists we don't know jejw")
        st.image("https://media1.tenor.com/m/FafJhrYbdZQAAAAd/sailor-moon-bishoujo-senshi-sailor-moon.gif")