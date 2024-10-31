import streamlit as st

st.title("FARS")

st.write("Welcome to the Facial Attendance Recognition System (FARS)!")
st.write("Please login or register to continue.")
if st.button("Login"):
    st.switch_page("pages/login.py")
if st.button("Register"):
    st.switch_page("pages/register.py")

st.write("Credits:")
col1, col2, col3 = st.columns(3)
with col1:
    st.write("Data Analysts:")
    c1, c2 = st.columns(2)
    with c1:
        st.write("• Sonia Mendia")
        st.write("• Christopher Cumi")
with col2:
    st.write("Data Engineers:")
    c1, c2 = st.columns(2)
    with c1:
        st.write("• Juan Fernandez")
        st.write("• Carlo Ek")
with col3:
    st.write("Data Engineers:")
    c1, c2 = st.columns(2)
    with c1:
        st.write("• Miguel Bastarrachea")
        st.write("• Yahir Sulu")