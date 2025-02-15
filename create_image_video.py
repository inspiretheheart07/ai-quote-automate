import os
import random
import tempfile
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from moviepy import *  # for video creation
from PIL import Image, ImageDraw, ImageFont, ImageFilter


# Authenticate using API Key
def authenticate_google_drive(api_key):
    # Build the Google Drive API client
    service = build('drive', 'v3', developerKey=api_key)
    return service


# Download file from Google Drive using file ID
def download_file_from_drive(file_id, destination_path, api_key):
    service = authenticate_google_drive(api_key)
    request = service.files().get_media(fileId=file_id)
    # Open file in write-binary mode and attempt to download
    with open(destination_path, 'wb') as f:
        try:
            request.execute()
            print(f"Successfully downloaded file to {destination_path}")
        except Exception as e:
            print(f"Error downloading file: {e}")
            raise


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
def text_on_background(text, background_image_path, font_path, output_image_path, line_height=15, shadow_offset=(5, 5)):
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

    video.write_videofile(output_video_path, codec='libx264', audio_codec='aac')

    return output_video_path


# Example usage

# Define your Google API Key here
api_key = os.getenv('GCP_API_KEY')

# Create a temporary directory using tempfile for safe file handling
with tempfile.TemporaryDirectory() as temp_dir:
    try:
        # Paths for temporary image and font files
        bg_image_path = os.path.join(temp_dir, 'bg.png')
        font_path = os.path.join(temp_dir, 'font.ttf')
        output_image_path = os.path.join(temp_dir, 'output_image.png')
        output_video_path = os.path.join(temp_dir, 'output_video.mp4')

        # Download the background image (bg.png) from Google Drive
        bg_image_file_id = '1mUohoXSVJPlrF4U0TUxztOnBo2saoTZv'  # Replace with the file ID of your background image in Google Drive
        download_file_from_drive(bg_image_file_id, bg_image_path, api_key)

        # Download the font (font.ttf) from Google Drive
        font_file_id = '1UKJRvJfEomWjImvRCA9K5rywnvYWs7Rf'  # Replace with the file ID of your font in Google Drive
        download_file_from_drive(font_file_id, font_path, api_key)

        # Text to overlay
        text = "Inspiring Quote: 'The best way to predict the future is to create it.'"

        # Generate an image with text overlay
        text_on_background(text, bg_image_path, font_path, output_image_path, line_height=20, shadow_offset=(5, 0))

        # Create a 55-second video with the image and a random music track
        music_folder = '/path/to/music/calm'  # Path to the folder with music files (e.g., calm folder in current folder)
        create_video_from_image_and_music(output_image_path, music_folder, output_video_path)

        # Upload the video to Google Drive (replace with the correct folder ID)
        drive_folder_id = '1-MvD1EumX_yChVWGhH6k34AAAP6REDhc'  # Replace with the correct folder ID in Google Drive
        uploaded_video_id = upload_file_to_drive(output_video_path, drive_folder_id, api_key)
        print(f"Video uploaded with ID: {uploaded_video_id}")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        raise
