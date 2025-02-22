import dropbox
import os

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN_DROP_BOX')
file_path = 'output_video.mp4'  # Path to the file you want to upload
dropbox_path = '/output_video.mp4'  # Path on Dropbox where the file will be stored

def delete_file():
    dbx = dropbox.Dropbox(ACCESS_TOKEN)
    try:
        # Delete the file from Dropbox
        dbx.files_delete_v2(dropbox_path)
        print(f"File at '{dropbox_path}' deleted from Dropbox.")
    except dropbox.exceptions.ApiError as e:
        print(f"Error deleting file from Dropbox: {e}")