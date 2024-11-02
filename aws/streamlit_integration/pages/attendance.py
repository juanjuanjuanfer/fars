import streamlit as st
import utils
from datetime import datetime

def main():
    # Page configuration
    st.set_page_config(
        page_title="Attendance Registration",
        page_icon=":memo:",
        layout="centered"
    )

    # Custom CSS for enhanced layout and style
    st.markdown("""
        <style>
        .main-title {
            font-size: 3rem;
            color: #003366;
            text-align: center;
            margin-bottom: 20px;
            font-weight: bold;
        }
        .section-title {
            font-size: 2rem;
            color: #2C3E50;
            margin-bottom: 15px;
            border-bottom: 2px solid #4A90E2;
            padding-bottom: 5px;
        }
        .info-box {
            background-color: #F0F4F7;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .button-primary {
            background-color: #4A90E2;
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 16px;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.3s;
            width: 100%;
        }
        .button-primary:hover {
            background-color: #357ABD;
        }
        .button-secondary {
            background-color: #95A5A6;
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 16px;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.3s;
            width: 100%;
        }
        .button-secondary:hover {
            background-color: #7F8C8D;
        }
        .retry-button {
            background-color: #E74C3C;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 14px;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .retry-button:hover {
            background-color: #C0392B;
        }
        .date-picker {
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize session state variables
    if 'stage' not in st.session_state:
        st.session_state.stage = 'ready'
    if 'processed_image' not in st.session_state:
        st.session_state.processed_image = None

    # Main title for the page
    st.markdown('<h1 class="main-title">Attendance Registration</h1>', unsafe_allow_html=True)

    # Check if a course is selected
    try:
        selected_course = st.session_state.selected_course
        with st.container():
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown(f"**Working with Course:**")
            st.markdown(f"**Course ID:** {selected_course['course_id']}<br>**Course Name:** {selected_course['course_name']}", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    except:
        st.warning("No course selected. Redirecting to login...")
        st.switch_page("pages/login.py")
        return

    # Button to select a different course
    if st.button("⬅️ Select Different Course"):
        st.session_state.selected_course = None
        st.switch_page("pages/courses.py")
        return

    # Function to reset the app state
    def reset_app():
        st.session_state.stage = 'ready'
        st.session_state.processed_image = None
        if 'detected_student' in st.session_state:
            del st.session_state.detected_student
        st.experimental_rerun()

    # Attendance registration stages
    if st.session_state.stage == 'ready':
        with st.container():
            st.markdown('<hr>')
            st.markdown('<h2 class="section-title">Start Attendance Registration</h2>', unsafe_allow_html=True)
            st.write("Click the button below to start capturing attendance.")
            if st.button("Start Capturing", key="start_btn", css_class="button-primary"):
                st.session_state.stage = 'capture'
                st.experimental_rerun()

    elif st.session_state.stage == 'capture':
        with st.container():
            st.markdown('<hr>')
            st.markdown('<h2 class="section-title">Capture Attendance</h2>', unsafe_allow_html=True)
            st.write("Please look at the camera and take a picture.")

            # Date selection for attendance
            selected_date = st.date_input(
                "Select attendance date",
                datetime.now().date(),
                max_value=datetime.now().date(),
                key="date_picker"
            )
            st.session_state.selected_date = selected_date

            # Camera input to capture a picture
            picture = st.camera_input("Take a picture")

            if picture:
                with st.spinner("Processing image..."):
                    # Process the image using a utility function
                    processed_image, error = utils.detect_and_process_face(picture.getvalue())

                    if error:
                        st.error(error)
                        if st.button("Retry Capture", key="retry_btn", css_class="retry-button"):
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
                            # Compare captured face to records
                            student_id, confidence = utils.compare_faces_rekognition(
                                rekognition,
                                picture.getvalue(),
                                "fars-bucket-v1",
                                selected_course['course_id']
                            )

                            if student_id:
                                # Get student name based on ID
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
                                st.experimental_rerun()
                            else:
                                st.error("No matching student found")
                                if st.button("Retry Capture", key="retry_btn_2", css_class="retry-button"):
                                    reset_app()

    elif st.session_state.stage == 'confirm':
        with st.container():
            st.markdown('<hr>')
            st.markdown('<h2 class="section-title">Confirm Attendance</h2>', unsafe_allow_html=True)

            student = st.session_state.detected_student

            # Information box showing detected student information
            st.markdown(f"""
                <div class="info-box">
                **Detected Student Information:**
                - **Name:** {student['name']}
                - **ID:** {student['id']}
                - **Match Confidence:** {student['confidence']:.2f}%
                - **Date:** {st.session_state.selected_date}
                </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Confirm Attendance", key="confirm_btn", css_class="button-primary"):
                    success, error = utils.register_attendance(
                        student['id'],
                        st.session_state.selected_course['course_id'],
                        'present',
                        st.session_state.selected_date
                    )

                    if error:
                        st.error(f"Error registering attendance: {error}")
                    else:
                        st.success("Attendance registered successfully!")
                        if st.button("Register Another Student", key="register_another_btn", css_class="button-primary"):
                            reset_app()

            with col2:
                if st.button("Not Correct", key="not_correct_btn", css_class="button-secondary"):
                    reset_app()

if __name__ == "__main__":
    main()