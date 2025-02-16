import os
import json
import random
import pygame
from moviepy import *
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Define the OAuth 2.0 scopes (Read-only access to Google Drive)
SCOPES = ['https://www.googleapis.com/auth/drive']  # Use drive.file scope to upload files
music_file = f"{random.randint(1, 11)}.mp3"
# Only download the background image, font, and a random music file
files_to_download = [music_file,'font.ttf', 'bg.png']

# Function to authenticate the user and load credentials from the environment variable (Service Account)
def authenticate():
    creds = None
    service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
    if not service_account_json:
        raise ValueError("Service account credentials JSON is not set.")
    
    credentials_data = json.loads(service_account_json)
    creds = service_account.Credentials.from_service_account_info(credentials_data, scopes=SCOPES)
    return creds

# Function to list files by names and download them
def download_files():
    creds = authenticate()
    drive_service = build('drive', 'v3', credentials=creds)
    for filename in files_to_download:
        try:
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
                if filename == 'bg.png':
                    text = "Your Custom Text Here"
                    font_path = 'font.ttf'
                    output_image_path = f"output_{filename}"
                    uploaded_image = text_on_background(text, filename, font_path, output_image_path)
                    video_path = create_video_with_music(uploaded_image)
                    upload_to_drive(video_path, drive_service)
        except Exception as e:
            print(f'An error occurred while downloading {filename}: {e}')

# Function to wrap text into multiple lines if necessary
def wrap_text(draw, text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line != "":
                lines.append(current_line.strip())
            current_line = word + " "

    if current_line != "":
        lines.append(current_line.strip())
    print(f"Lines to be drawn: {lines}")
    return lines

# Function to convert text to image with background and shadow
def text_on_background(text, background_image_path, font_path, output_image_path='output_image.png', line_height=15, shadow_offset=(5, 5)):
    image = Image.open(background_image_path)

    if image.mode != 'RGB':
        image = image.convert('RGB')

    image_width, image_height = image.size
    left = (image_width - 1080) // 2
    top = (image_height - 1920) // 2
    right = (image_width + 1080) // 2
    bottom = (image_height + 1920) // 2

    cropped_image = image.crop((left, top, right, bottom))

    draw = ImageDraw.Draw(cropped_image)

    padding_top = 140
    padding_bottom = 70
    padding_left = 10
    padding_right = 190

    available_width = cropped_image.width - padding_left - padding_right
    available_height = cropped_image.height - padding_top - padding_bottom

    font_size = 150
    font = ImageFont.truetype(font_path, font_size)

    while True:
        lines = wrap_text(draw, text, font, available_width)

        total_text_height = sum([draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines])
        total_text_height += (len(lines) - 1) * line_height

        if total_text_height <= available_height:
            break

        font_size -= 1
        font = ImageFont.truetype(font_path, font_size)

    lines = wrap_text(draw, text, font, available_width)

    total_text_height = sum([draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines])
    total_text_height += (len(lines) - 1) * line_height
    position_y = (cropped_image.height - total_text_height) // 2
    position_x = padding_left

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        position_x = (cropped_image.width - text_width) // 2

        shadow_position = (position_x + shadow_offset[0], position_y + shadow_offset[1])
        draw.text(shadow_position, line, fill=(50, 50, 50), font=font)

        draw.text((position_x, position_y), line, fill=(255, 255, 255), font=font)

        position_y += draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] + line_height

    sharpened_image = cropped_image.filter(ImageFilter.SHARPEN)

    sharpened_image.save(output_image_path, 'PNG')
    print(f"Image saved at: {output_image_path}")

    return output_image_path

# Create a 55-second video with background music
def create_video_with_music(image_path):
    creds = authenticate()
    drive_service = build('drive', 'v3', credentials=creds)
    
    try:
        # Check if the music file exists on Google Drive
        results = drive_service.files().list(q=f"name = '{music_file}'", fields="files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            raise FileNotFoundError(f"The music file '{music_file}' is missing from Drive!")
        
        file_id = items[0]['id']
        print(f"Downloading music file: {music_file} (ID: {file_id})")
        
        request = drive_service.files().get_media(fileId=file_id)
        fh = open(music_file, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")
        fh.close()
        
    except FileNotFoundError as e:
        print(e)
        return None
    except Exception as e:
        print(f"An error occurred while downloading the music file: {e}")
        return None

    try:
        # Load and trim the audio
        audio_clip = AudioFileClip(music_file)
        audio_clip = audio_clip.subclip(0, 55)
        
        # Create video
        image_clip = ImageClip(image_path, duration=55)

        # Set audio to the video
        video = image_clip.set_audio(audio_clip)

        # Write the video file to disk
        video_path = 'output_video.mp4'
        video.write_videofile(video_path, fps=24)
        return video_path
    except Exception as e:
        print(f"An error occurred while creating the video: {e}")
        return None

# Function to upload the image back to Google Drive
def upload_to_drive(image_path, drive_service):
    try:
        if not os.path.exists(image_path):
            print(f"File '{image_path}' does not exist!")
            return
    except Exception as e:
        print(f"Path doesn't exist: {e}")
    
    media = MediaFileUpload(image_path, mimetype='image/png')
    file_metadata = {'name': os.path.basename(image_path)}  # File name on Google Drive

    try:
        file = drive_service.files().create(
            media_body=media,
            body=file_metadata,
            fields='id'
        ).execute()

        print(f"File uploaded successfully: {file['name']} (ID: {file['id']})")
    except HttpError as e:
        print(f"An error occurred while uploading the file: {e}")

# Run the function to download files from Google Drive
if __name__ == '__main__':
    download_files()
