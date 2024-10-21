import boto3
import toml
from pathlib import Path

def read_config():
    """Read AWS configuration from .secrets/secrets.toml"""
    secrets_path = Path('fars/.secrets/secrets.toml')
    if not secrets_path.exists():
        raise FileNotFoundError("secrets.toml file not found in .secrets directory")
    
    config = toml.load(secrets_path)
    aws_config = config.get('aws', {})
    
    required_keys = ['aws_access_key_id', 'aws_secret_access_key', 'region', 'bucket_name']
    missing_keys = [key for key in required_keys if key not in aws_config]
    
    if missing_keys:
        raise KeyError(f"Missing required AWS configuration keys: {', '.join(missing_keys)}")
    
    return aws_config

def connect_to_s3(config):
    """Connect to AWS S3 bucket using provided configuration"""
    session = boto3.Session(
        aws_access_key_id=config['aws_access_key_id'],
        aws_secret_access_key=config['aws_secret_access_key'],
        region_name=config['region']
    )
    return session.resource('s3')

def list_bucket_contents(bucket_name, s3):
    """List all objects in specified S3 bucket"""
    try:
        bucket = s3.Bucket(bucket_name)
        print(f"\nContents of bucket '{bucket_name}':")
        for obj in bucket.objects.all():
            print(f"- {obj.key}")
    except Exception as e:
        print(f"Error accessing bucket: {str(e)}")

def main():
    try:
        # Read configuration
        config = read_config()
        
        # Connect to S3
        s3 = connect_to_s3(config)
        
        # List bucket contents
        list_bucket_contents(config['bucket_name'], s3)

        # get juli file from s3
        s3.Bucket(config['bucket_name']).download_file('juli.jpg', 'fars\\data\\external\\aws\\s3\\juli.jpg')
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()