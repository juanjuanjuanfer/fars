import streamlit as st
import mysql.connector
from mysql.connector import Error
import toml
import boto3
from io import BytesIO
import cv2
import numpy as np
from PIL import Image


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