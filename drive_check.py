import os
import json
import random
from moviepy.editor import *
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import google_auth_oauthlib.flow

# Define Google API scopes
SCOPES = ['https://www.googleapis.com/auth/drive']  # Drive scope for downloading files
YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube.upload']  # YouTube upload scope

# Define the files to be downloaded
music_file = f"{random.randint(1, 11)}.mp3"
files_to_download = [music_file, 'font.ttf', 'bg.png']

# Function to authenticate the user and load credentials from the environment variable (Service Account for Drive)
def authenticate():
    creds = None
    service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
    if not service_account_json:
        raise ValueError("Service account credentials JSON is not set.")
    
    credentials_data = json.loads(service_account_json)
    creds = service_account.Credentials.from_service_account_info(credentials_data, scopes=SCOPES)
    return creds

# OAuth 2.0 authentication for YouTube
def youtube_authenticate():
    credentials = None
    if os.path.exists('credentials.json'):
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            'credentials.json', YOUTUBE_SCOPES)
        credentials = flow.run_console()
    return credentials

# Function to upload a video to YouTube
def upload_video_to_youtube(video_path, credentials):
    try:
        youtube = build('youtube', 'v3', credentials=credentials)
        request_body = {
            'snippet': {
                'title': 'My Custom Video',
                'description': 'This is a custom video uploaded via the YouTube API.',
                'tags': ['custom', 'video', 'upload'],
                'categoryId': '22',  # '22' is the category ID for 'People & Blogs'
            },
            'status': {
                'privacyStatus': 'public',  # 'public', 'private', or 'unlisted'
            },
        }
        
        media = MediaFileUpload(video_path, mimetype='video/mp4', resumable=True)
        request = youtube.videos().insert(
            part='snippet,status',
            body=request_body,
            media_body=media
        )

        response = request.execute()
        print(f'Video uploaded successfully! Video ID: {response["id"]}')
    except Exception as e:
        print(f"An error occurred while uploading the video: {e}")

# Function to download a single file from Google Drive
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

# Function to list files by names and download them
def download_files():
    creds = authenticate()
    drive_service = build('drive', 'v3', credentials=creds)
    
    for file_name in files_to_download:
        try:
            download_file(drive_service, file_name)
        except Exception as e:
            print(f"Error downloading {file_name}: {e}")
            return None
    
    # Proceed with creating the video after successful downloads
    text = "Your Custom Text Here"
    output_image_path = f"output_bg_image.png"
    uploaded_image = text_on_background(text, 'bg.png', 'font.ttf', output_image_path)
    if uploaded_image:
        video_path = create_video_with_music(uploaded_image)
        if video_path:
            credentials = youtube_authenticate()  # Authenticate for YouTube
            upload_video_to_youtube(video_path, credentials)  # Upload to YouTube

# Function to create a 55-second video with background music using MoviePy
def create_video_with_music(image_path):
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        return None
    if not os.path.exists(music_file):
        print(f"Music file not found: {music_file}")
        return None

    try:
        # Load and trim the audio
        audio_clip = AudioFileClip(music_file).subclip(0, 55)       
        # Create video
        image_clip = ImageClip(image_path, duration=55)
        image_clip = image_clip.set_audio(audio_clip)
        # Write the video file to disk
        video_path = 'output_video.mp4'
        image_clip.write_videofile(video_path, fps=24)
        return video_path
    except Exception as e:
        print(f"An error occurred while creating the video: {e}")
        return None

# Start the process of downloading, creating video, and uploading to YouTube
download_files()
