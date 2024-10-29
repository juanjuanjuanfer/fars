import boto3
import streamlit as st
import toml
from io import BytesIO
import cv2
import numpy as np
from PIL import Image

def read_credentials():
    try:
        with open(".secrets/secrets.toml", "r") as f:
            s3_credentials = {
                "aws_access_key_id": "your-access-key-id",
                "aws_secret_access_key": "your-secret-access-key",
                "region_name": "your-region-name"
            }
            config = toml.load(f)
            s3_credentials.update(config["s3"])
            return s3_credentials
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

def main():
    # Initialize session state
    if 'stage' not in st.session_state:
        st.session_state.stage = 'capture'
    if 'processed_image' not in st.session_state:
        st.session_state.processed_image = None
    if 'original_image' not in st.session_state:
        st.session_state.original_image = None

    st.title("Face Image Upload to S3")

    def reset_app():
        st.session_state.stage = 'capture'
        st.session_state.processed_image = None
        st.session_state.original_image = None
        st.rerun()

    # Capture Stage
    if st.session_state.stage == 'capture':
        image_name = st.text_input("Enter image name")
        if not image_name:
            st.warning("Please enter an image name")
            return
        
        # Add file extension if not provided
        if not image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_name += '.jpg'
        
        picture = st.camera_input("Take a picture")
        
        if picture:
            st.session_state.original_image = picture
            processed_image, error = detect_and_process_face(picture.getvalue())
            
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
            credentials = read_credentials()
            if not credentials:
                if st.button("Retry"):
                    reset_app()
                return
            
            s3 = get_s3(credentials)
            if not s3:
                if st.button("Retry"):
                    reset_app()
                return
        
        # Convert PIL Image to bytes
        img_byte_arr = BytesIO()
        st.session_state.processed_image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        # Upload the image
        success = upload_to_s3(
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
