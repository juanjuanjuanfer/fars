import streamlit as st
import pymysql
from pymysql import Error
import toml
import boto3
from io import BytesIO
import cv2
import numpy as np
from PIL import Image
import datetime
from botocore.exceptions import ClientError


def read_db_credentials():
    try:
        with open(".streamlit/secrets.toml", "r") as f:
            creds = toml.load(f)["mysql"]
            return creds
    except Exception as e:
        st.error(f"Error reading database credentials: {str(e)}")
        return None
    
def get_db_connection():
    """Create database connection"""
    try:
        credentials = read_db_credentials()

        connection = pymysql.connect(
            host="bd-fars.cnamsmiius1y.us-east-1.rds.amazonaws.com",
            port=3306,
            user=credentials["user"],
            password=credentials["password"],
            database=credentials["database"],
            cursorclass=pymysql.cursors.DictCursor  # This enables dictionary cursors by default
        )
        if connection.open:
            print("Connected to MySQL database")
            return connection
            
    except Error as e:
        st.error(f"Error connecting to MySQL database: {str(e)}")
        return None
def get_courses(username):
    """
    Fetch courses from database with owner information, filtered by username
    """
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        with connection.cursor() as cursor:
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
        connection.close()



def read_credentials(option = "aws"):
    try:
        with open(".streamlit/secrets.toml", "r") as f:
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
        with connection.cursor() as cursor:
            query = "SELECT * FROM users WHERE user_username = %s AND user_password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            return user is not None

    except Error as e:
        st.error(f"Error verifying login: {str(e)}")
        return False

    finally:
        connection.close()



def get_student_list(course):
    connection = get_db_connection()
    if not connection:
        return []

    try:
        with connection.cursor() as cursor:
            query = "SELECT * FROM lists WHERE list_course_id = %s"
            cursor.execute(query, (course,))
            students = cursor.fetchall()
            return students

    except Error as e:
        st.error(f"Error fetching students: {str(e)}")
        return []

    finally:
        connection.close()


def check_student_exists(student_id):
    """
    Check if a student already exists in the database
    Returns: (exists, error_message)
    """
    connection = get_db_connection()
        
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT student_id FROM students WHERE student_id = %s", (student_id,))
            exists = cursor.fetchone() is not None
            return exists, None
    except Error as e:
        return False, f"Database query error: {str(e)}"
    finally:
        connection.close()

def register_student(student_id, student_name, student_email):
    """
    Register a new student in the database
    Returns: (success, error_message)
    """
    connection = get_db_connection()
        
    try:
        with connection.cursor() as cursor:
            sql = """INSERT INTO students (student_id, student_name, student_email) 
                     VALUES (%s, %s, %s)"""
            cursor.execute(sql, (student_id, student_name, student_email))
            connection.commit()
            return True, None
    except Error as e:
        return False, f"Failed to register student: {str(e)}"
    finally:
        connection.close()

def insert_student_into_list(student_id, course_id):
    """
    Insert a student into a course list
    Returns: (success, error_message)
    """
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            sql = """INSERT INTO lists (list_student_id, list_course_id)
                     VALUES (%s, %s)"""
            cursor.execute(sql, (student_id, course_id))
            connection.commit()
            return True, None
    except Error as e:
        return False, f"Failed to insert student into list: {str(e)}"
    finally:
        connection.close()

def register_user(user_name, user_username, user_password, user_email):
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            sql = """INSERT INTO users (user_name, user_username, user_password, user_email)
                     VALUES (%s, %s, %s, %s)"""
            cursor.execute(sql, (user_name, user_username, user_password, user_email))
            connection.commit()
            return True, None
    except Error as e:
        return False, f"Failed to register user: {str(e)}"
    finally:
        connection.close()

def verify_register(email):
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_email FROM users WHERE user_email = %s", (email,))
            exists = cursor.fetchone() is not None
            return exists
    except Error as e:
        return False, f"Database query error: {str(e)}"
    finally:
        connection.close()

def compare_faces_rekognition(rekognition_client, source_bytes, bucket_name, course_id):
    """
    Compare captured face with all student faces in the course
    Returns: (student_id, confidence) or (None, None) if no match
    """
    try:
        source_image = {'Bytes': source_bytes}
        
        connection = get_db_connection()
        if not connection:
            return None, None
            
        with connection.cursor() as cursor:
            cursor.execute("SELECT list_student_id FROM lists WHERE list_course_id = %s", (course_id,))
            students = cursor.fetchall()
        
        highest_similarity = 0
        matched_student = None
        
        for student in students:
            student_id = student['list_student_id']
            target_image = {'S3Object': {'Bucket': bucket_name, 'Name': f"{student_id}.jpg"}}
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
        if 'connection' in locals() and connection.open:
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
        with connection.cursor() as cursor:
            cursor.execute("SELECT student_name FROM students WHERE student_id = %s", (student_id,))
            result = cursor.fetchone()
            if result:
                return result['student_name'], None
            return None, "Student not found"
    except Error as e:
        return None, f"Database error: {str(e)}"
    finally:
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
        with connection.cursor() as cursor:
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
        connection.close()

def create_collection(rekognition_client, collection_id):
    """Create a Rekognition collection if it doesn't exist"""
    try:
        # Check if collection exists
        try:
            rekognition_client.describe_collection(CollectionId=collection_id)
            return True, None
        except rekognition_client.exceptions.ResourceNotFoundException:
            # Create new collection if it doesn't exist
            rekognition_client.create_collection(CollectionId=collection_id)
            return True, None
    except Exception as e:
        return False, str(e)

def process_face_image(image_bytes):
    """Process face image for optimal recognition"""
    try:
        # Convert bytes to PIL Image
        image = Image.open(BytesIO(image_bytes))
        
        # Convert to grayscale
        gray_image = image.convert('L')
        
        # Resize to standard size (adjust dimensions as needed)
        standard_size = (800, 800)
        resized_image = gray_image.resize(standard_size, Image.Resampling.LANCZOS)
        
        # Convert back to bytes
        img_byte_arr = BytesIO()
        resized_image.save(img_byte_arr, format='JPEG')
        
        return img_byte_arr.getvalue(), None
    except Exception as e:
        return None, str(e)

def check_face_quality(rekognition_client, image_bytes):
    """Check if face image meets quality standards"""
    try:
        response = rekognition_client.detect_faces(
            Image={'Bytes': image_bytes},
            Attributes=['ALL']
        )
        
        if not response['FaceDetails']:
            return False, "No face detected"
            
        face = response['FaceDetails'][0]
        
        # Check face quality metrics
        if face['Confidence'] < 90:
            return False, "Low confidence in face detection"
            
        if abs(face['Pose']['Yaw']) > 15:
            return False, "Face is turned too much to the side"
            
        if abs(face['Pose']['Pitch']) > 15:
            return False, "Face is tilted too much up or down"
            
        if face['Quality']['Brightness'] < 50:
            return False, "Image is too dark"
            
        if face['Quality']['Sharpness'] < 50:
            return False, "Image is not sharp enough"
            
        return True, None
        
    except Exception as e:
        return False, str(e)
    

def initialize_aws_services(credentials):
    """Initialize AWS services with proper error handling"""
    try:
        session = boto3.Session(
            aws_access_key_id=credentials['aws_access_key_id'],
            aws_secret_access_key=credentials['aws_secret_access_key'],
            region_name=credentials['region_name']
        )
        
        s3 = session.client('s3')
        rekognition = session.client('rekognition')
        
        # Test connections without listing all buckets
        # Test S3 access by trying to list the specific bucket
        try:
            s3.head_bucket(Bucket="fars-bucket-v1")
        except Exception as e:
            return None, None, f"S3 Bucket access error: {str(e)}"
            
        # Test Rekognition access
        try:
            rekognition.list_collections()
        except Exception as e:
            return None, None, f"Rekognition access error: {str(e)}"
        
        return s3, rekognition, None
    except Exception as e:
        return None, None, f"AWS initialization error: {str(e)}"
def create_collection(rekognition_client, collection_id):
    """Create a Rekognition collection if it doesn't exist"""
    try:
        rekognition_client.create_collection(CollectionId=collection_id)
        return True, None
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
            return True, None
        return False, str(e)

def index_faces_in_collection(rekognition_client, s3_client, bucket, collection_id, course_id):
    """Index all student faces from S3 into a Rekognition collection"""
    try:
        # Get list of student IDs for the course
        students = get_student_list(course_id)
        
        for student in students:
            student_id = student['list_student_id']
            image_key = f"{student_id}.jpg"
            
            try:
                # Check if image exists in S3
                s3_client.head_object(Bucket=bucket, Key=image_key)
                
                # Index face
                response = rekognition_client.index_faces(
                    CollectionId=collection_id,
                    Image={
                        'S3Object': {
                            'Bucket': bucket,
                            'Name': image_key
                        }
                    },
                    ExternalImageId=str(student_id),
                    MaxFaces=1,
                    QualityFilter="AUTO",
                    DetectionAttributes=['ALL']
                )
                
                if not response['FaceRecords']:
                    print(f"No face detected in image for student {student_id}")
                    
            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchKey':
                    print(f"Image not found for student {student_id}")
                else:
                    print(f"Error processing student {student_id}: {str(e)}")
                continue
                
        return True, None
    except Exception as e:
        return False, str(e)

def search_face_in_collection(rekognition_client, image_bytes, collection_id):
    """Search for a face in the Rekognition collection"""
    try:
        response = rekognition_client.search_faces_by_image(
            CollectionId=collection_id,
            Image={'Bytes': image_bytes},
            MaxFaces=1,
            FaceMatchThreshold=70
        )
        
        if response['FaceMatches']:
            match = response['FaceMatches'][0]
            student_id = match['Face']['ExternalImageId']
            confidence = match['Similarity']
            return student_id, confidence
            
        return None, None
        
    except ClientError as e:
        print(f"Error searching face: {str(e)}")
        return None, None

def verify_s3_bucket(s3_client, bucket_name):
    """Verify S3 bucket exists and is accessible"""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        return True, None
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            return False, f"Bucket {bucket_name} does not exist"
        elif error_code == '403':
            return False, f"No permission to access bucket {bucket_name}"
        return False, str(e)
    
# Add these to your utils.py

def get_attendance_count(course_id, date):
    """Get count of attendance records for a specific date"""
    connection = get_db_connection()
    if not connection:
        return 0
        
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM attendance 
                WHERE attendance_class_id = %s 
                AND attendance_date = %s
            """, (course_id, date))
            
            result = cursor.fetchone()
            return result['count'] if result else 0
        
    except Error as e:
        print(f"Error getting attendance count: {e}")
        return 0
    finally:
        connection.close()

def get_attendance_for_date(course_id, date):
    """Get all attendance records for a specific date"""
    connection = get_db_connection()
    if not connection:
        return None
        
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM attendance 
                WHERE attendance_class_id = %s 
                AND attendance_date = %s
            """, (course_id, date))
            
            return cursor.fetchall()
        
    except Error as e:
        print(f"Error getting attendance records: {e}")
        return None
    finally:
        connection.close()

def delete_attendance_for_date(course_id, date):
    """Delete all attendance records for a specific date"""
    connection = get_db_connection()
    if not connection:
        return False, "Database connection failed"
        
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM attendance 
                WHERE attendance_class_id = %s 
                AND attendance_date = %s
            """, (course_id, date))
            
            connection.commit()
            if cursor.rowcount > 0:
                return True, None
            else:
                return False, "No records found to delete"
            
    except Error as e:
        return False, f"Error deleting attendance records: {str(e)}"
    finally:
        connection.close()