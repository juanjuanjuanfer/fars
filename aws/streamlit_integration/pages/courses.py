import streamlit as st
import utils as utils

def create_new_course(course_name, owner_id):
    """Create a new course in the database"""
    connection = utils.get_db_connection()
    if not connection:
        return False, "Database connection failed"
        
    try:
        cursor = connection.cursor()
        
        # Check if course name already exists for this owner
        cursor.execute("""
            SELECT course_id FROM courses 
            WHERE course_name = %s AND course_owner = %s
        """, (course_name, owner_id))
        
        if cursor.fetchone():
            return False, "Course with this name already exists"
        
        # Insert new course
        cursor.execute("""
            INSERT INTO courses (course_name, course_owner)
            VALUES (%s, %s)
        """, (course_name, owner_id))
        
        connection.commit()
        return True, None
        
    except Exception as e:
        return False, f"Error creating course: {str(e)}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_user_id(username):
    """Get user ID from username"""
    connection = utils.get_db_connection()
    if not connection:
        return None
        
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT user_id FROM users WHERE user_username = %s", (username,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def main():
    st.title("Course Management")
    
    if 'username' not in st.session_state:
        st.error("Please login first.")
        st.switch_page("pages/login.py")
        return

    st.write(f"Welcome, {st.session_state.username}!")
    
    # Create tabs for course selection and creation
    select_tab, create_tab = st.tabs(["Select Course", "Create New Course"])
    
    with select_tab:
        # Initialize session state for selected course
        if 'selected_course' not in st.session_state:
            st.session_state.selected_course = None
        
        # Get courses from database for the logged-in user
        with st.spinner("Fetching courses..."):
            courses = utils.get_courses(st.session_state.username)
        
        if not courses:
            st.info("No courses found. Create a new course in the 'Create New Course' tab.")
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
            
            # Show course details in a card-like container
            st.markdown("---")
            st.markdown("### Course Details")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Course Information**")
                st.write(f"📚 Name: {selected_course['course_name']}")
                st.write(f"🔢 ID: {selected_course['course_id']}")
            
            with col2:
                st.markdown("**Teacher Information**")
                st.write(f"👤 Name: {selected_course['owner_name']}")
                st.write(f"📧 Email: {selected_course['owner_email']}")
            
            st.markdown("---")
            st.markdown("### Course Actions")
            
            # Create three columns for buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📝 Register Student", use_container_width=True):
                    st.switch_page("pages/student_registration.py")
            
            with col2:
                if st.button("✅ Take Attendance", use_container_width=True):
                    st.switch_page("pages/attendance.py")
            
            with col3:
                if st.button("📊 View Reports", use_container_width=True):
                    st.switch_page("pages/attendance_report.py")
    
    with create_tab:
        st.markdown("### Create New Course")
        st.write("Enter the details for your new course:")
        
        # Course creation form
        with st.form("create_course_form"):
            course_name = st.text_input(
                "Course Name",
                help="Enter a unique name for your course"
            )
            
            submit = st.form_submit_button("Create Course", type="primary")
            
            if submit:
                if not course_name:
                    st.error("Please enter a course name")
                    return
                    
                # Get user ID
                user_id = get_user_id(st.session_state.username)
                if not user_id:
                    st.error("Error getting user information")
                    return
                
                # Create course
                success, error = create_new_course(course_name, user_id)
                
                if success:
                    st.success("✨ Course created successfully!")
                    st.balloons()

                else:
                    st.error(f"Failed to create course: {error}")

if __name__ == "__main__":
    main()