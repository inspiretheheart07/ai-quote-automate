import boto3
import sys
import os
from botocore.exceptions import ClientError

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_DEFAULT_REGION')
AWS_FILE_S3_UPLOAD= os.getenv('AWS_FILE_S3_UPLOAD')

# Initialize the S3 client using boto3
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

bucket_name = os.getenv('AWS_DEFAULT_BUCKET') 



# Function to upload a file to the S3 bucket
def upload_file_to_s3():
    file_path = 'output_video.mp4' 
    object_name = 'output_video.mp4'
    print(f"Uploading {file_path} to S3 bucket {bucket_name}...")
    try:
        with open(file_path, 'rb') as data:
            s3_client.upload_fileobj(data, bucket_name, object_name)
        print(f"Upload completed: {file_path} uploaded to {bucket_name}/{object_name}")
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except ClientError as e:
        print(f"Error uploading file: {e}")
    return AWS_FILE_S3_UPLOAD

# Function to delete a file from the S3 bucket
def delete_file_from_s3(bucket_name, object_name):
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=object_name)
        print(f"File {object_name} deleted from bucket {bucket_name}.")
    except ClientError as e:
        print(f"Error deleting file: {e}")

# Function to delete the S3 bucket (if it's empty)
def delete_bucket(bucket_name):
    try:
        s3_client.delete_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} deleted.")
    except ClientError as e:
        print(f"Error deleting bucket: {e}")


