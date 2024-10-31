import streamlit as st
import utils
from datetime import datetime

def main():
    # Initialize session state
    if 'stage' not in st.session_state:
        st.session_state.stage = 'ready'
    if 'processed_image' not in st.session_state:
        st.session_state.processed_image = None

    st.title("Attendance Registration")

    # Verify course selection
    try:
        selected_course = st.session_state.selected_course
        st.write("Working with course:")
        st.write(f"Course ID: {selected_course['course_id']}")
        st.write(f"Course Name: {selected_course['course_name']}")
    except:
        st.switch_page("pages/login.py")
        return

    # Course selection button at the top
    if st.button("⬅️ Select Different Course"):
        st.session_state.selected_course = None
        st.switch_page("pages/courses.py")
        return

    def reset_app():
        st.session_state.stage = 'ready'
        st.session_state.processed_image = None
        if 'detected_student' in st.session_state:
            del st.session_state.detected_student
        st.rerun()

    # Ready Stage - Initial state with start button
    if st.session_state.stage == 'ready':
        st.markdown("---")
        st.markdown("### Start Attendance Registration")
        st.write("Click the button below to start capturing attendance.")
        if st.button("Start Capturing", type="primary", use_container_width=True):
            st.session_state.stage = 'capture'
            st.rerun()

    # Capture Stage
    elif st.session_state.stage == 'capture':
        st.markdown("---")
        st.markdown("### Capture Attendance")
        st.write("Please look at the camera and take a picture")
        
        # Add date selection
        selected_date = st.date_input(
            "Select attendance date",
            datetime.now().date(),
            max_value=datetime.now().date()
        )
        st.session_state.selected_date = selected_date
        
        # Camera input directly initialized in the capture stage
        picture = st.camera_input("Take a picture")
        
        if picture:
            with st.spinner("Processing image..."):
                # Process the image
                processed_image, error = utils.detect_and_process_face(picture.getvalue())
                
                if error:
                    st.error(error)
                    if st.button("Retry Capture"):
                        reset_app()
                else:
                    # Initialize AWS services
                    credentials = utils.read_credentials(option="aws")
                    if not credentials:
                        st.error("Failed to read AWS credentials")
                        return
                        
                    rekognition = utils.get_rekognition(credentials)
                    if not rekognition:
                        st.error("Failed to initialize Rekognition")
                        return
                    
                    with st.spinner("Matching face..."):
                        # Compare faces
                        student_id, confidence = utils.compare_faces_rekognition(
                            rekognition,
                            picture.getvalue(),
                            "fars-bucket-v1",
                            selected_course['course_id']
                        )
                        
                        if student_id:
                            # Get student name
                            student_name, error = utils.get_student_name(student_id)
                            if error:
                                st.error(f"Error getting student name: {error}")
                                return
                                
                            st.session_state.detected_student = {
                                'id': student_id,
                                'name': student_name,
                                'confidence': confidence
                            }
                            st.session_state.stage = 'confirm'
                            st.rerun()
                        else:
                            st.error("No matching student found")
                            if st.button("Retry Capture"):
                                reset_app()

    # Confirm Stage
    elif st.session_state.stage == 'confirm':
        st.markdown("---")
        st.markdown("### Confirm Attendance")
        
        student = st.session_state.detected_student
        
        # Create an info box
        st.info(f"""
        📋 **Detected Student Information:**
        * Name: {student['name']}
        * ID: {student['id']}
        * Match Confidence: {student['confidence']:.2f}%
        * Date: {st.session_state.selected_date}
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirm Attendance", type="primary", use_container_width=True):
                success, error = utils.register_attendance(
                    student['id'],
                    st.session_state.selected_course['course_id'],
                    'present',
                    st.session_state.selected_date
                )
                
                if error:
                    st.error(f"Error registering attendance: {error}")
                else:
                    st.success("✨ Attendance registered successfully!")
                    if st.button("Register Another Student", use_container_width=True):
                        reset_app()
                        
        with col2:
            if st.button("❌ Not Correct", type="secondary", use_container_width=True):
                reset_app()

if __name__ == "__main__":
    main()
