import streamlit as st
import mysql.connector
from mysql.connector import Error
import toml
import boto3
from io import BytesIO
import cv2
import numpy as np
from PIL import Image
import datetime


def read_db_credentials():
    try:
        with open(".secrets/secrets.toml", "r") as f:
            creds = toml.load(f)["mysql"]
            return creds
    except Exception as e:
        st.error(f"Error reading database credentials: {str(e)}")
        return None
    
def get_db_connection():
    """Create database connection"""
    try:
        credentials = read_db_credentials()

        connection = mysql.connector.connect(
            host="bd-fars.cnamsmiius1y.us-east-1.rds.amazonaws.com",
            port=3306,
            user=credentials["user"],
            password=credentials["password"],
            database=credentials["database"]
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
            
    except Error as e:
        st.error(f"Error connecting to MySQL database: {str(e)}")
        return None

def get_courses(username):
    """
    Fetch courses from database with owner information, filtered by username
    
    Args:
        username (str): Username from session state to filter courses
        
    Returns:
        list: List of courses belonging to the specified user
    """
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        # Updated query to join courses with users table and filter by username
        query = """
        SELECT 
            c.course_id,
            c.course_name,
            c.course_owner,
            u.user_name as owner_name,
            u.user_email as owner_email,
            u.user_username as owner_username
        FROM courses c
        LEFT JOIN users u ON c.course_owner = u.user_id
        WHERE u.user_username = %s
        """
        cursor.execute(query, (username,))
        courses = cursor.fetchall()
        return courses
    
    except Error as e:
        st.error(f"Error fetching courses: {str(e)}")
        return []
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def read_credentials(option = "aws"):
    try:
        with open(".secrets/secrets.toml", "r") as f:
            aws_credentials = {
                "aws_access_key_id": "your-access-key-id",
                "aws_secret_access_key": "your-secret-access-key",
                "region_name": "your-region-name"
            }
            config = toml.load(f)
            aws_credentials.update(config[option])
            return aws_credentials
    except Exception as e:
        st.error(f"Error reading credentials: {str(e)}")
        return None

def get_s3(credentials):
    try:
        return boto3.client("s3", **credentials)
    except Exception as e:
        st.error(f"Error connecting to S3: {str(e)}")
        return None

def get_rekognition(credentials):
    try:
        return boto3.client('rekognition', **credentials)
    except Exception as e:
        st.error(f"Error connecting to Rekognition: {str(e)}")
        return None

def detect_and_process_face(image_bytes):
    try:
        # Convert image bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Load the cascade classifier
        face_cascade = cv2.CascadeClassifier('aws/streamlit_integration/models/haarcascade_frontalface_default.xml')
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return None, "No face detected"
        
        # Get the first face
        x, y, w, h = faces[0]
        
        # Add padding around the face
        padding = 30
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(w + 2*padding, img.shape[1] - x)
        h = min(h + 2*padding, img.shape[0] - y)
        
        # Crop the face
        face = img[y:y+h, x:x+w]
        
        # Convert to grayscale
        gray_face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        
        # Convert back to PIL Image
        pil_image = Image.fromarray(gray_face)
        
        return pil_image, None
        
    except Exception as e:
        return None, f"Error processing image: {str(e)}"

def upload_to_s3(picture_data, bucket, image_name, s3_client):
    try:
        # Convert the picture data to BytesIO
        picture_bytes = BytesIO(picture_data)
        
        # Create a status container
        with st.status("Uploading image to S3...", expanded=True) as status:
            status.write("Starting upload...")
            
            # Upload the file
            s3_client.upload_fileobj(picture_bytes, bucket, image_name)
            
            status.write("Upload completed successfully!")
            status.update(label="Upload complete!", state="complete")
            
        return True
    except Exception as e:
        st.error(f"Error uploading to S3: {str(e)}")
        return False
    

def verify_login(username, password):
    connection = get_db_connection()
    if not connection:
        return False

    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE user_username = %s AND user_password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        return user is not None

    except Error as e:
        st.error(f"Error verifying login: {str(e)}")
        return False

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_student_list(course):
    connection = get_db_connection()
    if not connection:
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM lists WHERE list_course_id = %s"
        cursor.execute(query, (course,))
        students = cursor.fetchall()
        return students

    except Error as e:
        st.error(f"Error fetching students: {str(e)}")
        return []

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def check_student_exists(student_id):
    """
    Check if a student already exists in the database
    Returns: (exists, error_message)
    """
    connection = get_db_connection()
        
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT student_id FROM students WHERE student_id = %s", (student_id,))
        exists = cursor.fetchone() is not None
        return exists, None
    except Error as e:
        return False, f"Database query error: {str(e)}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def register_student(student_id, student_name, student_email):
    """
    Register a new student in the database
    Returns: (success, error_message)
    """
    connection = get_db_connection()

        
    try:
        cursor = connection.cursor()
        sql = """INSERT INTO students (student_id, student_name, student_email) 
                 VALUES (%s, %s, %s)"""
        cursor.execute(sql, (student_id, student_name, student_email))
        connection.commit()
        return True, None
    except Error as e:
        return False, f"Failed to register student: {str(e)}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def insert_student_into_list(student_id, course_id):
    """
    Insert a student into a course list
    Returns: (success, error_message)
    """
    connection = get_db_connection()


    try:
        cursor = connection.cursor()
        sql = """INSERT INTO lists (list_student_id, list_course_id)
                 VALUES (%s, %s)"""
        cursor.execute(sql, (student_id, course_id))
        connection.commit()
        return True, None
    except Error as e:
        return False, f"Failed to insert student into list: {str(e)}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def register_user(user_name,user_username,user_password,user_email):
    connection = get_db_connection()

    try:
        cursor = connection.cursor()
        sql = """INSERT INTO users (user_name, user_username, user_password, user_email)
                 VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql, (user_name, user_username, user_password, user_email))
        connection.commit()
        return True, None
    except Error as e:
        return False, f"Failed to register user: {str(e)}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def verify_register(email):
    connection = get_db_connection()

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT user_email FROM users WHERE user_email = %s", (email ))
        exists = cursor.fetchone() is not None
        return exists
    except Error as e:
        return False, f"Database query error: {str(e)}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def compare_faces_rekognition(rekognition_client, source_bytes, bucket_name, course_id):
    """
    Compare captured face with all student faces in the course
    Returns: (student_id, confidence) or (None, None) if no match
    """
    try:
        # Convert the source image bytes to required format
        source_image = {'Bytes': source_bytes}
        
        # Get all students in the course
        connection = get_db_connection()
        if not connection:
            return None, None
            
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT list_student_id FROM lists WHERE list_course_id = %s", (course_id,))
        students = cursor.fetchall()
        
        highest_similarity = 0
        matched_student = None
        
        # Compare with each student's image
        for student in students:
            student_id = student['list_student_id']
            target_image = {'S3Object': {'Bucket': bucket_name, 'Name': f"{student_id}.jpg"}}
            print(target_image)
            try:
                response = rekognition_client.compare_faces(
                    SourceImage=source_image,
                    TargetImage=target_image,
                    SimilarityThreshold=70
                )
                
                if response['FaceMatches']:
                    similarity = response['FaceMatches'][0]['Similarity']
                    if similarity > highest_similarity:
                        highest_similarity = similarity
                        matched_student = student_id
                        
            except Exception as e:
                print(f"Error comparing with student {student_id}: {str(e)}")
                continue
                
        return matched_student, highest_similarity
        
    except Exception as e:
        print(f"Error in face comparison: {str(e)}")
        return None, None
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def get_student_name(student_id):
    """
    Get student name from database
    Returns: (student_name, error_message)
    """
    connection = get_db_connection()
    if not connection:
        return None, "Database connection failed"
        
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT student_name FROM students WHERE student_id = %s", (student_id,))
        result = cursor.fetchone()
        if result:
            return result['student_name'], None
        return None, "Student not found"
    except Error as e:
        return None, f"Database error: {str(e)}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def register_attendance(student_id, course_id, status, date=None):
    """
    Register attendance in database
    Returns: (success, error_message)
    """
    if date is None:
        date = datetime.now().date()
        
    connection = get_db_connection()
    if not connection:
        return False, "Database connection failed"
        
    try:
        cursor = connection.cursor()
        
        # Check if attendance already registered for this date
        cursor.execute("""
            SELECT * FROM attendance 
            WHERE attendance_date = %s 
            AND attendance_student_id = %s 
            AND attendance_class_id = %s
        """, (date, student_id, course_id))
        
        if cursor.fetchone():
            return False, "Attendance already registered for this date"
        
        # Insert new attendance record
        sql = """INSERT INTO attendance 
                (attendance_date, attendance_student_id, attendance_class_id, attendance_status)
                VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql, (date, student_id, course_id, status))
        connection.commit()
        return True, None
    except Error as e:
        return False, f"Failed to register attendance: {str(e)}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()