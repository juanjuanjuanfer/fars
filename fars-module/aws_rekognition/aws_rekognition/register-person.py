from utils import *

import toml
def register_person():
    # register a person uploading a photo taken by the camera and naming it with the person's name, then upload the photo to s3
    # Load secrets from .secrets/secrets.toml
    secrets = toml.load('fars/.secrets/secrets.toml')
    bucket_name = secrets['bucket']["bucketname"]

    try:
        # Capture image from camera
        print("Waiting for camera capture...")
        image = capture_image_with_opencv()
        print("Image captured successfully")
        image_bytes = image_to_bytes(image)

        # Upload image to S3
        image_name = input("Enter your name: ")
        image_key = f"{image_name}.jpg"
        upload_image_to_s3(bucket_name, image_key, image_bytes)
        print("Image uploaded successfully")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    register_person()