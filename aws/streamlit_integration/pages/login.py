import streamlit as st
import utils
import requests

# Giphy API configuration
GIPHY_CONFIG = {
    "base_url": "https://api.giphy.com/v1/gifs/random",
    "api_key": "0UTRbFtkMxAplrohufYco5IY74U8hOes",
    "tag": "cat",
    "rating": "g"
}
sorry = {
    "base_url": "https://api.giphy.com/v1/gifs/random",
    "api_key": "0UTRbFtkMxAplrohufYco5IY74U8hOes",
    "tag": "sorry",
    "rating": "g"
}

def get_random_giphy_gif(set=GIPHY_CONFIG):
    """Fetch a random GIF from Giphy API"""
    try:
        url = (f"{set['base_url']}?"
               f"api_key={GIPHY_CONFIG['api_key']}&"
               f"tag={set['tag']}&"
               f"rating={GIPHY_CONFIG['rating']}")
        
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200 and 'data' in data:
            return data['data']['images']['original']['url']
        return None
    except:
        return None

st.set_page_config(
    page_title="FARS Login",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session states
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_gif' not in st.session_state:
    st.session_state.current_gif = get_random_giphy_gif()

st.title("FARS Login")

col1, col2, col3, col4, col5 = st.columns(5)

# Login column
with col1:
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
                st.switch_page("pages/courses.py")
            else:
                st.error("Who tf are you?")
                st.image("https://i.pinimg.com/736x/a8/21/23/a82123800eb40b9ec8055939e4ff549c.jpg")
    else:
        st.success(f"Already logged in as {st.session_state.username}")
        st.switch_page("pages/courses.py")

# Reset Password column
with col3:
    st.write("Forgot your password?")
    if st.button("Reset Password"):
        st.write("Contact the admin to reset your password hehe")
        st.image(get_random_giphy_gif(set=sorry))

# Register column
with col4:
    st.write("Don't have an account?")
    if st.button("Register"):
        st.switch_page("pages/register.py")

# Cat GIF column
with col5:
    st.write("Don't know what to do?")
    if st.button("Show me a kitty! 🐱"):
        new_gif = get_random_giphy_gif()
        if new_gif:
            st.session_state.current_gif = new_gif
    
    if st.session_state.current_gif:
        st.image(st.session_state.current_gif, use_column_width=True)
    else:
        st.image("https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif", use_column_width=True)