from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from .authenticate import authenticate

def download_file(drive_service, filename):
    results = drive_service.files().list(q=f"name = '{filename}'", fields="files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print(f'No file found with the name: {filename}')
    else:
        file_id = items[0]['id']
        print(f'Downloading file: {filename} (ID: {file_id})')
        request = drive_service.files().get_media(fileId=file_id)
        fh = open(filename, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")
        fh.close()
        print(f'{filename} downloaded successfully.')

def download_files(scopes=None):
    # Authenticate and get credentials
    creds = authenticate(scopes=scopes)    
    # Check if creds are valid before proceeding
    if creds:
        try:
            # Build the Google Drive service using the credentials
            drive_service = build('drive', 'v3', credentials=creds)
            files_to_download = ["file1.mp3", "font.ttf", "bg.png"]  # Modify your files as needed
            
            # Iterate through each file and try to download
            for file_name in files_to_download:
                try:
                    download_file(drive_service, file_name)
                except Exception as e:
                    print(f"Error downloading {file_name}: {e}")
        except Exception as e:
            print(f"An error occurred while building the Google Drive service: {e}")
    else:
        print("Authentication failed. No credentials found.")
    