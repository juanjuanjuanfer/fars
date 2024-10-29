import boto3
import streamlit as st
import toml


def read_credentials():
    with open(".secrets/secrets.toml","r") as f:
        s3_credentials = {
        "aws_access_key_id": "your-access-key-id",
        "aws_secret_access_key": "your-secret-access-key",
        "region_name": "your-region-name"
        }
        print(s3_credentials.update(toml.load(f)["s3"]))
        return s3_credentials.update(toml.load(f)["s3"])

def get_s3(credentials):
    return boto3.client("s3", **credentials)

def get_rekognition(credentials):
    return boto3.client('rekognition', **credentials)


image_name = st.text_input("Enter image name")

# Display camera input
picture = st.camera_input("Take a picture")


# If a picture is taken, display it
if picture:
    st.image(picture)
    credentials = read_credentials()
    s3 = get_s3(credentials)
    s3.upload_fileobj(picture, "fars-bucket-v1", image_name)
    st.write("Done")

