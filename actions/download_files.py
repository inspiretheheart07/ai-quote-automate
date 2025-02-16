from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload,MediaFileUpload  
from .authenticate import authenticate

def list_and_filter_files(drive_service, extensions=None):
    try:
        # List all files in Google Drive
        results = drive_service.files().list(fields="files(id, name)").execute()
        items = results.get('files', [])
        
        if not items:
            print("No files found.")
            return []
        
        print("All files in your Google Drive:")
        for item in items:
            print(f"{item['name']} (ID: {item['id']})")

        # Filter files based on the given extensions
        if extensions:
            filtered_files = [item for item in items if any(item['name'].endswith(ext) for ext in extensions)]
            print("\nFiltered files:")
            for file in filtered_files:
                print(f"{file['name']} (ID: {file['id']})")
            return filtered_files
        
        return items

    except HttpError as error:
        print(f"An error occurred: {error}")
        return []

def download_file(drive_service, filename):
    try:
        # Search for the file by its name
        query = f"name = '{filename}'"  # Exact match for the file name
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print(f'No file found with the name: {filename}')
            return None

        file_id = items[0]['id']
        print(f'Found file: {filename} (ID: {file_id})')
        
        # Download the file
        request = drive_service.files().get_media(fileId=file_id)
        with open(filename, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}%.")
        print(f'{filename} downloaded successfully.')
        return filename

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

# Example usage:
def download_files(scopes=None,files_to_download):
    creds = authenticate(scopes=scopes)    
    if creds:
        try:
            # Build the Google Drive service using credentials
            drive_service = initialize_drive_service(scopes=scopes,creds=creds)
            for file_name in files_to_download:
                try:
                     download_file(drive_service, file_name)
                except Exception as e:
                     print(f"Error downloading {file_name}: {e}")
                     return None
    else:
        print("Authentication failed. No credentials found.")
