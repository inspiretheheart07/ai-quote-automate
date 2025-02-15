import os
from googleapiclient.discovery import build

# Use your API key here
API_KEY = os.getenv('GCP_API_KEY')

# Build the service object using the API key
drive_service = build('drive', 'v3', developerKey=API_KEY)

# Example: List the files in your Google Drive
results = drive_service.files().list().execute()
items = results.get('files', [])

if not items:
    print('No files found.')
else:
    print('Files:')
    for item in items:
        print(f'{item["name"]} ({item["id"]})')
