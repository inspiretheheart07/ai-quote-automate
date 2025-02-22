import dropbox
import os

# Replace with your access token
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN_DROP_BOX')
file_path = 'output_video.mp4'  # Path to the file you want to upload
dropbox_path = '/output_video.mp4'  # Path on Dropbox where the file will be stored

# Initialize Dropbox client
dbx = dropbox.Dropbox(ACCESS_TOKEN)

# Function to upload a file to Dropbox
def upload_file():
    with open(file_path, 'rb') as f:
        # Upload the file to Dropbox
        dbx.files_upload(f.read(), dropbox_path, mute=True)
        print(f"File '{file_path}' uploaded to Dropbox at '{dropbox_path}'.")
        return create_shared_link(dropbox_path)

# Function to create a shared link and modify it for direct download
def create_shared_link(dropbox_path):
    try:
        # Create shared link
        shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path)
        
        # Modify the link to be a direct download link by replacing 'dl=0' with 'dl=1'
        direct_link = shared_link_metadata.url.replace("?dl=0", "?dl=1")
        print(f"Direct link: {direct_link}")
        return f'{direct_link}&raw=1'
    except dropbox.exceptions.ApiError as e:
        print(f"Error creating shared link: {e}")
        return None
