from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import json
# Define the OAuth 2.0 scopes (Read-only access to Google Drive)
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate():
    creds = None
    # Load service account credentials from the secret
    service_account_info = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)

    return creds

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

if __name__ == '__main__':
    list_files()
