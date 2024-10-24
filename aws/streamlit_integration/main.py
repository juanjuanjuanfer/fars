
# to use camera on http site, you must include the site on chrome settings, so go to <chrome://flags/#unsafely-treat-insecure-origin-as-secure> 
#enable it and type the url befor using it.

import streamlit as st

st.title("Webcam Capture with Streamlit")

# Display camera input
picture = st.camera_input("Take a picture")

# If a picture is taken, display it
if picture:
    st.image(picture)
