import boto3
import streamlit as st
import toml
from io import BytesIO

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
    st.title("Image Upload to S3")
    
    # Get image name
    image_name = st.text_input("Enter image name")
    if not image_name:
        st.warning("Please enter an image name")
        return
    
    # Add file extension if not provided
    if not image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
        image_name += '.jpg'
    
    # Display camera input
    picture = st.camera_input("Take a picture")
    
    # If a picture is taken
    if picture:
        # Show the captured image
        st.image(picture)
        
        # Create a container for the upload process
        with st.container():
            # Initialize S3 connection
            with st.spinner("Initializing S3 connection..."):
                credentials = read_credentials()
                if not credentials:
                    return
                
                s3 = get_s3(credentials)
                if not s3:
                    return
            
            # Upload the image
            success = upload_to_s3(
                picture.getvalue(),
                "fars-bucket-v1",
                image_name,
                s3
            )
            
            if success:
                st.success(f"Image '{image_name}' successfully uploaded to S3!")
            else:
                st.error("Failed to upload image. Please try again.")

if __name__ == "__main__":
    main()
