# pages/01_select_class.py
import streamlit as st
import mysql.connector
from mysql.connector import Error
import toml

def read_db_credentials():
    try:
        with open(".secrets/secrets.toml", "r") as f:
            return toml.load(f)["mysql"]
    except Exception as e:
        st.error(f"Error reading database credentials: {str(e)}")
        return None

def get_db_connection():
    """Create database connection"""
    try:
        credentials = read_db_credentials()
        if not credentials:
            return None
        
        connection = mysql.connector.connect(
            host="bd-fars.cnamsmiius1y.us-east-1.rds.amazonaws.com",
            port=3306,
            user=credentials.get("user", "admin"),
            password=credentials.get("password"),
            database=credentials.get("database")
        )
        
        if connection.is_connected():
            return connection
            
    except Error as e:
        st.error(f"Error connecting to MySQL database: {str(e)}")
        return None

def get_courses():
    """Fetch all courses from database"""
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM courses")  # Keeping table name as 'classes' but selecting course fields
        courses = cursor.fetchall()
        return courses
    
    except Error as e:
        st.error(f"Error fetching courses: {str(e)}")
        return []
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def main():
    st.title("Course Selection")
    
    # Initialize session state for selected course
    if 'selected_course' not in st.session_state:
        st.session_state.selected_course = None
    
    # Get courses from database
    with st.spinner("Fetching courses from database..."):
        courses = get_courses()
    
    if not courses:
        st.error("No courses found or unable to fetch courses.")
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
    
    # Store selected course in session state
    if selected_course_name:
        selected_course = next((c for c in courses if c['course_name'] == selected_course_name), None)
        st.session_state.selected_course = selected_course
        
        # Show selected course details
        st.write("Selected course details:")
        st.write(f"Course ID: {selected_course['course_id']}")
        st.write(f"Course Name: {selected_course['course_name']}")
        st.write(f"Course Owner: {selected_course['course_owner']}")
        
        # Button to navigate to next page
        if st.button("Continue with selected course"):
            st.switch_page("pages/02_process_class.py")

if __name__ == "__main__":
    main()

# pages/02_process_class.py
import streamlit as st

def main():
    st.title("Process Course")
    
    # Check if course is selected
    if 'selected_course' not in st.session_state or not st.session_state.selected_course:
        st.error("No course selected. Please select a course first.")
        if st.button("Go to course selection"):
            st.switch_page("pages/01_select_class.py")
        return
    
    # Display selected course information
    st.write("Working with course:")
    selected_course = st.session_state.selected_course
    st.write(f"Course ID: {selected_course['course_id']}")
    st.write(f"Course Name: {selected_course['course_name']}")
    st.write(f"Course Owner: {selected_course['course_owner']}")
    
    # Add your processing logic here
    
    # Button to go back to course selection
    if st.button("Select different course"):
        st.session_state.selected_course = None
        st.switch_page("pages/01_select_class.py")

if __name__ == "__main__":
    main()
