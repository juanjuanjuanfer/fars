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

def get_classes():
    """Fetch all classes from database"""
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM courses")
        classes = cursor.fetchall()
        return classes
    
    except Error as e:
        st.error(f"Error fetching classes: {str(e)}")
        return []
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def main():
    st.title("Class Selection")
    
    # Initialize session state for selected class
    if 'selected_class' not in st.session_state:
        st.session_state.selected_class = None
    
    # Get classes from database
    with st.spinner("Fetching classes from database..."):
        classes = get_classes()
    
    if not classes:
        st.error("No classes found or unable to fetch classes.")
        if st.button("Retry"):
            st.rerun()
        return
    
    # Create selectbox with class names
    class_names = [c['name'] if isinstance(c, dict) else c[1] for c in classes]  # Adjust index based on your table structure
    selected_class_name = st.selectbox(
        "Select a class:",
        options=class_names,
        index=None,
        placeholder="Choose a class..."
    )
    
    # Store selected class in session state
    if selected_class_name:
        selected_class = next((c for c in classes if (c['name'] if isinstance(c, dict) else c[1]) == selected_class_name), None)
        st.session_state.selected_class = selected_class
        
        # Show selected class details
        st.write("Selected class details:")
        st.json(selected_class)
        
        # Button to navigate to next page
        if st.button("Continue with selected class"):
            st.switch_page("pages/02_process_class.py")

if __name__ == "__main__":
    main()

# pages/02_process_class.py
import streamlit as st

def main():
    st.title("Process Class")
    
    # Check if class is selected
    if 'selected_class' not in st.session_state or not st.session_state.selected_class:
        st.error("No class selected. Please select a class first.")
        if st.button("Go to class selection"):
            st.switch_page("pages/01_select_class.py")
        return
    
    # Display selected class information
    st.write("Working with class:")
    st.json(st.session_state.selected_class)
    
    # Add your processing logic here
    
    # Button to go back to class selection
    if st.button("Select different class"):
        st.session_state.selected_class = None
        st.switch_page("pages/01_select_class.py")

if __name__ == "__main__":
    main()