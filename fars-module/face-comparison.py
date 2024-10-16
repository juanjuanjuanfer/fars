import utils
import toml

def main():
    """Main function"""
    # Load secrets from .secrets/secrets.toml
    secrets = toml.load('fars/.secrets/secrets.toml')
    bucket_name = secrets['bucket']["bucketname"]
    
    try:
        # Get list of images from bucket
        bucket_images = utils.get_bucket_images(bucket_name)
        if bucket_images is None:
            return

        # Capture image from camera
        print("Waiting for camera capture...")
        image1 = utils.capture_image_with_opencv()
        print("Image captured successfully")
        image1_bytes = utils.image_to_bytes(image1)

        # Compare with each image in bucket
        for image in bucket_images:
            image_key = image['Key']
            print(f"Processing image: {image_key}")
            
            image2 = utils.get_image_from_s3(bucket_name, image_key)
            if image2 is None:
                print(f"Skipping {image_key} due to download/processing error")
                continue
                
            try:
                image2_bytes = utils.image_to_bytes(image2)
                response = utils.compare_faces(image1_bytes, image2_bytes)
                
                if response and 'FaceMatches' in response and response['FaceMatches']:
                    print(f"Match found: {image_key}")
                    similarity = response['FaceMatches'][0]['Similarity']
                    print(f"Similarity: {similarity}%")
                    return
                
            except Exception as e:
                print(f"Error processing comparison for {image_key}: {e}")
                continue

        print("No match found")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()