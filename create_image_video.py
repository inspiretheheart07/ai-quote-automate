import os
import random
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from moviepy import *  # for video creation
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests

# Authenticate using API Key
def authenticate_google_drive(api_key):
    # Build the Google Drive API client
    service = build('drive', 'v3', developerKey=api_key)
    return service

# Alternative function to download file using requests
def download_file_with_requests(file_id, destination_path, api_key):
    service = authenticate_google_drive(api_key)
    
    # Get the download URL
    request = service.files().get_media(fileId=file_id)
    request_uri = request.uri
    
    # Make the request using requests library to fetch the file
    response = requests.get(request_uri, headers={'Authorization': f'Bearer {api_key}'}, stream=True)
    print(f"Successfully downloaded file to {request_uri}")
    if response.status_code == 200:
        with open(destination_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print(f"Successfully downloaded file to {destination_path}")
    else:
        print(f"Error: Could not download file (status code: {response.status_code})")
        raise Exception(f"Failed to download file {file_id}")

# Upload file to Google Drive
def upload_file_to_drive(file_path, drive_folder_id, api_key):
    service = authenticate_google_drive(api_key)
    
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [drive_folder_id]
    }
    media = MediaFileUpload(file_path, mimetype='application/octet-stream')
    
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

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
    
    return lines

# Function to convert text to image with background and shadow
def text_on_background(text, background_image_path, font_path, output_image_path='/tmp/output_image.png', line_height=15, shadow_offset=(5, 5)):
    try:
        image = Image.open(background_image_path)
        image.verify()  # Verify that the image is valid
        print(f"Image {background_image_path} is valid.")
    except Exception as e:
        print(f"Error opening image {background_image_path}: {e}")
        raise
    
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
    sharpened_image.save(output_image_path)

    return output_image_path

# Function to create a video from image and music
def create_video_from_image_and_music(image_path, music_folder, output_video_path):
    music_files = [f"{music_folder}/{i}.mp3" for i in range(1, 12)]
    music_file = random.choice(music_files)

    audio = AudioFileClip(music_file)
    audio = audio.subclip(0, 55)

    image_clip = ImageClip(image_path, duration=55)
    image_clip = image_clip.resize(height=1920)

    video = image_clip.set_audio(audio)
    video = video.set_fps(24)

    video.write_videofile(output_video_path, codec='libx264', audio_codec='aac',threads=4, preset='ultrafast',  ffmpeg_params=['-crf', '23', '-pix_fmt', 'yuv420p'])

    return output_video_path

# Example usage

# Define your Google API Key here
api_key = os.getenv('GCP_API_KEY')

# Download the background image (bg.png) from Google Drive
bg_image_file_id = '1mUohoXSVJPlrF4U0TUxztOnBo2saoTZv'  # Replace with the file ID of your background image in Google Drive
bg_image_path = '/tmp/tmp92xrigtk/bg.png'

# Use the alternative download method
try:
    download_file_with_requests(bg_image_file_id, bg_image_path, api_key)
except Exception as e:
    print(f"Failed to download background image: {e}")

# Download the font (font.ttf) from Google Drive
font_file_id = '1UKJRvJfEomWjImvRCA9K5rywnvYWs7Rf'  # Replace with the file ID of your font in Google Drive
font_path = '/tmp/tmp92xrigtk/font.ttf'

# Use the alternative download method for font file
try:
    download_file_with_requests(font_file_id, font_path, api_key)
except Exception as e:
    print(f"Failed to download font file: {e}")

# Text to overlay
text = "Inspiring Quote: 'The best way to predict the future is to create it.'"

# Generate an image with text overlay
output_image_path = '/tmp/tmp92xrigtk/output_image.png'
try:
    output_image_path = text_on_background(text, bg_image_path, font_path, output_image_path, line_height=20, shadow_offset=(5, 0))
except Exception as e:
    print(f"Failed to generate image: {e}")

# Create a 55-second video with the image and a random music track
output_video_path = '/tmp/tmp92xrigtk/output_video.mp4'
music_folder = '/path/to/music/calm'  # Path to the folder with music files (e.g., calm folder in current folder)
try:
    create_video_from_image_and_music(output_image_path, music_folder, output_video_path)
except Exception as e:
    print(f"Failed to create video: {e}")

# Upload the video to Google Drive (replace with the correct folder ID)
drive_folder_id = '1-MvD1EumX_yChVWGhH6k34AAAP6REDhc'  # Replace with the correct folder ID in Google Drive
try:
    uploaded_video_id = upload_file_to_drive(output_video_path, drive_folder_id, api_key)
    print(f"Video uploaded with ID: {uploaded_video_id}")
except Exception as e:
    print(f"Failed to upload video: {e}")
