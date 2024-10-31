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
        image_name = st.text_input("Enter student id")

        # verify if student not already on course
        if not image_name:
            st.warning("Please enter an image name")
            return
        
        # Add file extension if not provided
        if not image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_name += '.jpg'
        
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
            st.success(f"Image '{st.session_state.image_name}' successfully uploaded to S3!")
            if st.button("Start New Capture"):
                reset_app()
        else:
            st.error("Failed to upload image.")
            if st.button("Retry Upload"):
                st.session_state.stage = 'upload'
                st.rerun()

if __name__ == "__main__":
    main()
