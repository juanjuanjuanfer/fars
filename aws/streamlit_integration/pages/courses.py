import streamlit as st
import utils as utils
import sys
import os

# Add the parent directory to sys.path if utils.py is in the parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

def main():
    # Page configuration
    st.set_page_config(
        page_title="FARS Course Selection",
        page_icon="📚",
        layout="centered"
    )
    
    # Custom CSS for enhanced styling
    st.markdown("""
        <style>
        /* General background */
        body {
            background-color: #f0f2f6;
        }
        /* Course selection container */
        .course-container {
            background-color: #ffffff;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            max-width: 700px;
            margin: auto;
        }
        /* Main title */
        .main-title {
            font-size: 2.5rem;
            color: #003366; /* Primary blue */
            text-align: center;
            margin-bottom: 20px;
            font-weight: bold;
        }
        /* Subtitle */
        .subtitle {
            font-size: 1rem;
            color: #7f8c8d; /* Gray color */
            text-align: center;
            margin-bottom: 30px;
        }
        /* Selectbox styling */
        .stSelectbox>div>div>select {
            border-radius: 5px;
            padding: 10px;
            border: 1px solid #ccc;
        }
        /* Buttons */
        .stButton>button {
            background-color: #4A90E2; /* Primary blue */
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
        /* Secondary button (Go to Attendance) */
        .stButton.secondary>button {
            background-color: #2980b9; /* Secondary blue */
        }
        .stButton.secondary>button:hover {
            background-color: #1c5980; /* Darker secondary blue on hover */
        }
        /* Success and warning messages */
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
        /* Course details section */
        .course-details {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Course selection form container
    with st.container():
        st.markdown('<div class="course-container">', unsafe_allow_html=True)
        st.markdown('<h1 class="main-title">Course Selection</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Select a course to manage attendance and student registrations</p>', unsafe_allow_html=True)
    
        # Check if the user is logged in
        if 'username' not in st.session_state:
            st.error("Please log in first.")
            st.button("Go to Login", key="goto_login", css_class="secondary", on_click=lambda: st.switch_page("pages/login.py"))
            st.markdown('</div>', unsafe_allow_html=True)
            return
    
        st.success(f"Welcome, **{st.session_state.username}**!")
    
        # Initialize session state for selected course
        if 'selected_course' not in st.session_state:
            st.session_state.selected_course = None
    
        # Fetch courses from the database
        with st.spinner("Fetching courses from the database..."):
            courses = utils.get_courses(st.session_state.username)
    
        if not courses:
            st.warning("No courses found for your account.")
            if st.button("Retry", key="retry_fetch"):
                st.experimental_rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            return
    
        # Create a selectbox with course names
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
    
            # Display selected course details with owner information
            st.markdown('<div class="course-details">', unsafe_allow_html=True)
            st.markdown("### Selected Course Details")
            col1, col2 = st.columns(2)
    
            with col1:
                st.markdown("**Course Information:**")
                st.write(f"• **Course Name:** {selected_course['course_name']}")
    
            with col2:
                st.markdown("**Owner Information:**")
                st.write(f"• **Owner Name:** {selected_course['owner_name']}")
                st.write(f"• **Owner Email:** {selected_course['owner_email']}")
            st.markdown('</div>', unsafe_allow_html=True)
    
            # Navigation buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Register Student", key="register_student"):
                    st.switch_page("pages/student_registration.py")
            with col2:
                if st.button("Take Attendance", key="take_attendance", css_class="secondary"):
                    st.switch_page("pages/attendance.py")
    
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
