import os
import json
import pickle
import random
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Define the OAuth 2.0 scopes (Read-only access to Google Drive)
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Files to download from Google Drive (specify names or pattern)
files_to_download = ['bg.png', 'font.ttf', f'{random.randint(1, 11)}.mp3']

# Function to authenticate the user and load credentials from the environment variable
def authenticate():
    creds = None
    # Check if the token.pickle file exists for storing credentials
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If credentials are invalid or don't exist, request new authentication
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Load credentials from the environment variable (this should be your `credentials.json`)
            credentials_json = os.getenv('GOOGLE_CREDENTIALS')
            if not credentials_json:
                raise ValueError("Environment variable GOOGLE_CREDENTIALS is not set.")
            
            # Parse the JSON string from the environment variable
            credentials_data = json.loads(credentials_json)

            # Initialize the flow for the first-time authentication
            flow = InstalledAppFlow.from_client_config(credentials_data, SCOPES)

            # Run the local server to authenticate the user and get the refresh token
            creds = flow.run_local_server(port=0)

        # Save the credentials to token.pickle for future use
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

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
