import streamlit as st
import utils
from datetime import datetime


def verify_teacher_password(password):
    """Verify if the entered password matches the course owner's password"""
    try:
        username = st.session_state.selected_course['owner_username']
        return utils.verify_login(username, password)
    except Exception as e:
        st.error(f"Error verifying password: {e}")
        return False

def process_missing_attendance(course_id, date):
    """Mark all students without attendance as absent"""
    # Get all students in the course
    students = utils.get_student_list(course_id)
    if not students:
        return False, "No students found in this course"
    
    # Get students who already have attendance
    present_students = utils.get_attendance_for_date(course_id, date)
    if not present_students:
        present_students = []
    
    present_ids = [student['attendance_student_id'] for student in present_students]
    
    # Mark absent for students without attendance
    success_count = 0
    error_count = 0
    
    for student in students:
        student_id = student['list_student_id']
        if student_id not in present_ids:
            success, error = utils.register_attendance(
                student_id,
                course_id,
                'absent',
                date
            )
            if success:
                success_count += 1
            else:
                error_count += 1
    
    return True, f"Processed {success_count} absences. {error_count} errors."

def delete_date_attendance(course_id, date):
    """Delete all attendance records for a specific date"""
    success, error = utils.delete_attendance_for_date(course_id, date)
    return success, error


def main():
    st.title("Attendance Registration")

    # Check if user is logged in and has selected a course
    if 'selected_course' not in st.session_state:
        st.warning("Please select a course first")
        if st.button("Go to Course Selection"):
            st.switch_page("pages/courses.py")
        return

    # Display current course info
    course = st.session_state.selected_course
    st.write("**Current Course:**")
    st.write(f"📚 {course['course_name']} (ID: {course['course_id']})")
    
    # Course selection button
    if st.button("⬅️ Change Course"):
        st.session_state.selected_course = None
        st.switch_page("pages/courses.py")
        return

    st.markdown("---")

    # Date selection
    selected_date = st.date_input(
        "Select Date",
        datetime.now().date(),
        max_value=datetime.now().date()
    )

    # Camera input
    st.write("📸 Take a photo for attendance")
    image = st.camera_input("Take photo")

    if image:
        with st.spinner("Processing image..."):
            # Initialize AWS services
            credentials = utils.read_credentials(option="aws")
            if not credentials:
                st.error("Could not read AWS credentials")
                return

            s3, rekognition, error = utils.initialize_aws_services(credentials)
            if error:
                st.error(f"AWS Error: {error}")
                return

            # Process face image
            processed_image, error = utils.detect_and_process_face(image.getvalue())
            if error:
                st.error(f"Face detection error: {error}")
                return

            # Search face in collection
            collection_id = f"course_{course['course_id']}"
            try:
                response = rekognition.search_faces_by_image(
                    CollectionId=collection_id,
                    Image={'Bytes': image.getvalue()},
                    MaxFaces=1,
                    FaceMatchThreshold=70
                )

                if not response['FaceMatches']:
                    st.error("❌ No matching student found in this course")
                    return

                # Get the best match
                match = response['FaceMatches'][0]
                student_id = match['Face']['ExternalImageId']
                confidence = match['Similarity']

                # Get student name
                student_name, error = utils.get_student_name(student_id)
                if error:
                    st.error(f"Error getting student info: {error}")
                    return

                # Show match results
                st.success("✅ Student found!")
                st.info(f"""
                ### Detected Student:
                - **Name:** {student_name}
                - **ID:** {student_id}
                - **Match Confidence:** {confidence:.2f}%
                """)

                # Confirmation buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Confirm Attendance", type="primary", use_container_width=True):
                        success, error = utils.register_attendance(
                            student_id,
                            course['course_id'],
                            'present',
                            selected_date
                        )
                        
                        if error:
                            if "already registered" in error:
                                st.warning("⚠️ Student already registered attendance for today")
                            else:
                                st.error(f"Error registering attendance: {error}")
                        else:
                            st.success("✨ Attendance registered successfully!")
                            st.balloons()

                with col2:
                    if st.button("❌ Not Correct", type="secondary", use_container_width=True):
                        st.rerun()

            except rekognition.exceptions.ResourceNotFoundException:
                st.error("No face collection found for this course. Please register students first.")
            except rekognition.exceptions.InvalidParameterException:
                st.error("Could not detect a clear face in the image. Please try again.")
            except Exception as e:
                st.error(f"Error processing image: {str(e)}")
    st.markdown("---")
    st.markdown("### 📊 Attendance Management")
    
    # Create tabs for different management options
    manage_tab, delete_tab = st.tabs(["Complete Attendance", "Delete Attendance"])
    
    with manage_tab:
        st.write("Complete attendance for a specific date by marking absent all students without attendance.")
        manage_date = st.date_input(
            "Select date to complete",
            datetime.now().date(),
            max_value=datetime.now().date(),
            key="manage_date"
        )
        
        # Check if date already completed
        attendance_count = utils.get_attendance_count(course['course_id'], manage_date)
        student_count = len(utils.get_student_list(course['course_id']))
        
        if attendance_count == student_count:
            st.warning(f"✅ Attendance for {manage_date} is already complete!")
        else:
            missing_count = student_count - attendance_count
            st.info(f"ℹ️ {missing_count} students without attendance for {manage_date}")
            
            if st.button("Complete Attendance", type="primary"):
                password = st.text_input("Enter your password to confirm", type="password")
                if st.button("Confirm"):
                    if verify_teacher_password(password):
                        with st.spinner("Processing missing attendance..."):
                            success, message = process_missing_attendance(
                                course['course_id'],
                                manage_date
                            )
                            if success:
                                st.success(f"✅ {message}")
                                st.balloons()
                            else:
                                st.error(f"❌ Error: {message}")
                    else:
                        st.error("❌ Invalid password")
    
    with delete_tab:
        st.write("Delete all attendance records for a specific date.")
        delete_date = st.date_input(
            "Select date to delete",
            datetime.now().date(),
            max_value=datetime.now().date(),
            key="delete_date"
        )
        
        # Show current attendance count for selected date
        current_count = utils.get_attendance_count(course['course_id'], delete_date)
        if current_count > 0:
            st.info(f"ℹ️ {current_count} attendance records found for {delete_date}")
            

            password = st.text_input("Enter your password to confirm deletion", type="password", key="delete_password")
            if st.button("Confirm Deletion"):
                if verify_teacher_password(password):
                    with st.spinner("Deleting attendance records..."):
                        success, error = delete_date_attendance(
                            course['course_id'],
                            delete_date
                        )
                        if success:
                            st.success("✅ Attendance records deleted successfully!")
                        else:
                            st.error(f"❌ Error: {error}")
                else:
                    st.error("❌ Invalid password")
        else:
            st.warning(f"No attendance records found for {delete_date}")

if __name__ == "__main__":
    main()