import os
import json
import pickle
import random
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Define the OAuth 2.0 scopes (Read-only access to Google Drive)
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Files to download from Google Drive (with random number in the filename)
random_number = random.randint(1, 11)  # Generate a random number between 1 and 11
files_to_download = ['bg.png', 'font.ttf', f'{random_number}.mp3']  # Add random file name

# Function to authenticate the user and load credentials from the environment variable (Service Account)
def authenticate():
    creds = None
    # Get the service account credentials JSON from the environment variable
    service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
    if not service_account_json:
        raise ValueError("Service account credentials JSON is not set.")
    
    # Parse the service account JSON string
    credentials_data = json.loads(service_account_json)

    # Use service account credentials to authenticate
    creds = service_account.Credentials.from_service_account_info(credentials_data, scopes=SCOPES)

    return creds

# Function to list files by names and download them
def download_files():
    creds = authenticate()

    # Build the Drive API service
    drive_service = build('drive', 'v3', credentials=creds)

    for filename in files_to_download:
        try:
            # Search for the file by name
            results = drive_service.files().list(q=f"name = '{filename}'", fields="files(id, name)").execute()
            items = results.get('files', [])

            if not items:
                print(f'No file found with the name: {filename}')
            else:
                file_id = items[0]['id']
                print(f'Downloading file: {filename} (ID: {file_id})')

                # Get the file's content and download it
                request = drive_service.files().get_media(fileId=file_id)
                fh = open(filename, 'wb')

                # Use MediaIoBaseDownload to download the file
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print(f"Download {int(status.progress() * 100)}%.")
                
                fh.close()
                print(f'{filename} downloaded successfully.')
        
        except Exception as e:
            print(f'An error occurred while downloading {filename}: {e}')

# Run the function to download files from Google Drive
if __name__ == '__main__':
    download_files()
