import os
import json
import random
from moviepy import AudioFileClip, ImageClip
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Define the OAuth 2.0 scopes (Read-only access to Google Drive)
SCOPES = ['https://www.googleapis.com/auth/drive']

# Define the files to be downloaded
music_file = f"{random.randint(1, 11)}.mp3"
files_to_download = [music_file, 'font.ttf', 'bg.png']

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
            upload_to_drive(video_path, drive_service)

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
    if not os.path.exists(background_image_path):
        print(f"Background image not found: {background_image_path}")
        return None
    
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
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        return None
    if not os.path.exists(music_file):
        print(f"Music file not found: {music_file}")
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

# Function to upload the image back to Google Drive (implementation omitted for brevity)
def upload_to_drive(video_path, drive_service):
    pass

# Start the process
download_files()
