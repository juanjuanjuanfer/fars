import streamlit as st
from io import BytesIO
import utils



def main():
    # Initialize session state
    if 'stage' not in st.session_state:
        st.session_state.stage = 'capture'
    if 'processed_image' not in st.session_state:
        st.session_state.processed_image = None
    if 'original_image' not in st.session_state:
        st.session_state.original_image = None

    st.title("Student Registration")

    
    try:
        
        selected_course = st.session_state.selected_course
        st.write("Working with course:")
        st.write(f"Course ID: {selected_course['course_id']}")
        st.write(f"Course Name: {selected_course['course_name']}")
        st.write(f"Course Owner: {selected_course['course_owner']}")
    except:
        st.switch_page("pages/login.py")
        return

    if st.button("Select different course"):
        st.session_state.selected_course = None
        st.switch_page("pages/courses.py")

    def reset_app():
        st.session_state.stage = 'capture'
        st.session_state.processed_image = None
        st.session_state.original_image = None
        st.rerun()

    # Capture Stage
    if st.session_state.stage == 'capture':
        student_id = st.text_input("Enter student ID")
        
        if student_id:
            # First check if student exists in course
            student_list = utils.get_student_list(selected_course['course_id'])
            if student_list:
                for x in student_list:
                    if x['list_student_id'] == int(student_id):
                        st.warning("Student already registered in this course")
                        reset_app()
                        return
            
            # Then check if student exists in database
            exists, error = utils.check_student_exists(student_id)
            if error:
                st.error(f"Error checking student: {error}")
                return
                
            # If student doesn't exist, collect additional information
            if not exists:
                student_name = st.text_input("Enter student name")
                student_email = st.text_input("Enter student email")
                
                if student_name and student_email:
                    # Register the student in the database
                    success, error = utils.register_student(student_id, student_name, student_email)
                    if error:
                        st.error(f"Error registering student: {error}")
                        return
                    if not success:
                        st.error("Failed to register student")
                        return
            
            # Add file extension for the image
            image_name = f"{student_id}.jpg"
            
            picture = st.camera_input("Take a picture")
            
            if picture:
                st.session_state.original_image = picture
                processed_image, error = utils.detect_and_process_face(picture.getvalue())
                
                if error:
                    st.error(error)
                    if st.button("Retry"):
                        reset_app()
                else:
                    st.session_state.processed_image = processed_image
                    st.session_state.image_name = image_name
                    st.session_state.student_id = student_id
                    st.session_state.stage = 'review'
                    st.rerun()

    # Review Stage
    elif st.session_state.stage == 'review':
        st.write("Review processed image:")
        st.image(st.session_state.processed_image, caption="Processed Face Image")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Accept Image"):
                st.session_state.stage = 'upload'
                st.rerun()
        with col2:
            if st.button("Retry Capture"):
                reset_app()

    # Upload Stage
    elif st.session_state.stage == 'upload':
        # Initialize S3 connection
        with st.spinner("Initializing S3 connection..."):
            credentials = utils.read_credentials(option="s3")
            if not credentials:
                if st.button("Retry"):
                    reset_app()
                return
            
            s3 = utils.get_s3(credentials)
            if not s3:
                if st.button("Retry"):
                    reset_app()
                return
        
        # Convert PIL Image to bytes
        img_byte_arr = BytesIO()
        st.session_state.processed_image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        # Upload the image
        success = utils.upload_to_s3(
            img_byte_arr,
            "fars-bucket-v1",
            st.session_state.image_name,
            s3
        )
        
        if success:
            # Register student in the course
            success, error = utils.insert_student_into_list(
                st.session_state.student_id,
                selected_course['course_id']
            )
            if error:
                st.error(f"Error registering student in course: {error}")
            elif not success:
                st.error("Failed to register student in course")
            else:
                st.success(f"Student successfully registered and image uploaded!")
            
            if st.button("Start New Registration"):
                reset_app()
        else:
            st.error("Failed to upload image.")
            if st.button("Retry Upload"):
                st.session_state.stage = 'upload'
                st.rerun()

if __name__ == "__main__":
    main()
