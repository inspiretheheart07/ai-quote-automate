import os
import json
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the OAuth 2.0 scopes (Read-only access to Google Drive)
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

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

# Function to list all files from Google Drive
def list_files():
    creds = authenticate()

    # Build the Drive API service
    drive_service = build('drive', 'v3', credentials=creds)

    # Call the Drive API to list files
    results = drive_service.files().list().execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(f'{item["name"]} ({item["id"]})')

# Run the function to list files from Google Drive
if __name__ == '__main__':
    list_files()
