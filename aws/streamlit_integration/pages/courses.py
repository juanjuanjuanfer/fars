import streamlit as st
import utils as utils

def main():
    st.title("Course Selection")
    
    if 'username' not in st.session_state:
        st.error("Please login first.")
        st.switch_page("pages/login.py")
        return

    st.write(f"Welcome, {st.session_state.username}!")
    # Initialize session state for selected course
    if 'selected_course' not in st.session_state:
        st.session_state.selected_course = None
    
    # Get courses from database for the logged-in user
    with st.spinner("Fetching courses from database..."):
        courses = utils.get_courses(st.session_state.username)
    
    if not courses:
        st.warning("No courses found for your account.")
        if st.button("Retry"):
            st.rerun()
        return
    
    # Create selectbox with course names
    course_names = [c['course_name'] for c in courses]
    selected_course_name = st.selectbox(
        "Select a course:",
        options=course_names,
        index=None,
        placeholder="Choose a course..."
    )
    
    # Store selected course in session state and display details
    if selected_course_name:
        selected_course = next((c for c in courses if c['course_name'] == selected_course_name), None)
        st.session_state.selected_course = selected_course
        
        # Show selected course details with owner information
        st.write("Selected course details:")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Course Information:")
            st.write(f"• Course Name: {selected_course['course_name']}")
        
        with col2:
            st.write("Owner Information:")
            st.write(f"• Owner Name: {selected_course['owner_name']}")
            st.write(f"• Owner Email: {selected_course['owner_email']}")
        
        # Button to navigate to next page
        if st.button("Register Student"):
            st.switch_page("pages/student_registration.py")
        
        if st.button("Take Attendance"):
            st.switch_page("pages/attendance.py")

if __name__ == "__main__":
    main()