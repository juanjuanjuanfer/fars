import boto3
from botocore.exceptions import ClientError
import cv2
import numpy as np
import toml


def connect_to_s3():
    """Create a connection to S3"""
    credentials = {
        "aws_access_key_id": "<YOUR_AwsAccessKey_HERE>",
        "aws_secret_access_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "region_name": "us-east-1"    }
    # read credentials from .secrets/secrets.toml
    with open("fars\\.secrets\\secrets.toml", "r") as f:
        credentials = toml.load(f)["aws"]

    s3 = boto3.client('s3', **credentials)
    return s3

def get_bucket_images(bucket_name):
    """Get a list of images in a bucket"""
    s3 = connect_to_s3()
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        if 'Contents' not in response:
            print(f"No objects found in bucket {bucket_name}")
            return None
        # Filter for image files only
        contents = [item for item in response['Contents'] 
                   if item['Key'].lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not contents:
            print("No image files found in bucket")
            return None
        return contents
    except ClientError as e:
        print(f"Error accessing bucket: {e}")
        return None

def connect_to_rekognition():
    """Create a connection to Rekognition"""
    credentials = {
        "aws_access_key_id": "<YOUR_AwsAccessKey_HERE>",
        "aws_secret_access_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "region_name": "us-east-1",
        "bucket_name": "bucket"    }
    # read credentials from .secrets/secrets.toml
    with open("fars\\.secrets\\secrets.toml", "r") as f:
        credentials = toml.load(f)["reko"]
    rekognition = boto3.client('rekognition', **credentials)
    return rekognition

def capture_image_with_opencv():
    """Capture an image using OpenCV"""
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        raise ValueError("Could not open camera")
    
    while True:
        return_value, image = camera.read()
        if not return_value:
            raise ValueError("Could not read frame from camera")
        
        cv2.imshow('Press Space to capture', image)
        if cv2.waitKey(1) & 0xFF == ord(' '):  # Wait for space key to capture
            break
    
    camera.release()
    cv2.destroyAllWindows()
    return image

def image_to_bytes(image):
    """Convert an image to bytes"""
    if image is None:
        raise ValueError("Input image is None")
    
    is_success, buffer = cv2.imencode(".jpg", image)
    if not is_success:
        raise ValueError("Could not encode image to bytes")
    return buffer.tobytes()

def compare_faces(image1, image2):
    """Compare two faces using Rekognition"""
    rekognition = connect_to_rekognition()
    try:
        response = rekognition.compare_faces(
            SourceImage={'Bytes': image1},
            TargetImage={'Bytes': image2},
            SimilarityThreshold=90
        )
        return response
    except ClientError as e:
        print(f"Error comparing faces: {e}")
        return None

def get_image_from_s3(bucket_name, image_key):
    """Get an image from S3"""
    s3 = connect_to_s3()
    try:
        response = s3.get_object(Bucket=bucket_name, Key=image_key)
        image_bytes = response['Body'].read()
        
        # Decode image
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            print(f"Failed to decode image: {image_key}")
            return None
            
        return image
    except ClientError as e:
        print(f"Error downloading image {image_key}: {e}")
        return None
    except Exception as e:
        print(f"Error processing image {image_key}: {e}")
        return None


def upload_image_to_s3(bucket_name, image_key, image_bytes):
    """Upload an image to S3"""
    s3 = connect_to_s3()
    try:
        s3.put_object(Bucket=bucket_name, Key=image_key, Body=image_bytes)
    except ClientError as e:
        print(f"Error uploading image {image_key}: {e}")
        return None
    except Exception as e:
        print(f"Error processing image {image_key}: {e}")
        return None