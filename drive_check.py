import os
import json
import random
import traceback 
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from PIL import Image, ImageDraw, ImageFont, ImageFilter  # For adding text to the image

# Define the OAuth 2.0 scopes (Read-only access to Google Drive)
SCOPES = ['https://www.googleapis.com/auth/drive']  # Use drive.file scope to upload files

# Only download the background image and font
files_to_download = ['font.ttf','bg.png' ]

# Function to authenticate the user and load credentials from the environment variable (Service Account)
def authenticate():
    creds = None
    # Get the service account credentials JSON from the environment variable
    service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
    if not service_account_json:
        raise ValueError("Service account credentials JSON is not set.")
    
    # Parse the service account JSON string
    credentials_data = json.loads(service_account_json)

    # Use service account credentials to authenticate
    creds = service_account.Credentials.from_service_account_info(credentials_data, scopes=SCOPES)

    return creds

# Function to list files by names and download them
def download_files():
    creds = authenticate()

    # Build the Drive API service
    drive_service = build('drive', 'v3', credentials=creds)

    try:
        results1 = drive_service.files().list(fields="files(id, name)").execute()
        items1 = results1.get('files', [])

        if not items1:
            print('No files found in the Drive.')
        else:
            print('Files found in the Drive:')
            for item in items1:
                print(f'{item["name"]} (ID: {item["id"]})')    
    except Exception as e:
        print(f"Error listing files: {e}")

    for filename in files_to_download:
        try:
            results = drive_service.files().list(q=f"name = '{filename}'", fields="files(id, name)").execute()
            items = results.get('files', [])

            if not items:
                print(f'No file found with the name: {filename}')
            else:
                file_id = items[0]['id']
                print(f'Downloading file: {filename} (ID: {file_id})')

                # Get the file's content and download it
                request = drive_service.files().get_media(fileId=file_id)
                fh = open(filename, 'wb')

                # Use MediaIoBaseDownload to download the file
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print(f"Download {int(status.progress() * 100)}%.")
                
                fh.close()
                print(f'{filename} downloaded successfully.')

                if filename == 'bg.png':  # Check if it's the background image
                    text = "Your Custom Text Here"
                    font_path = 'font.ttf'  # Path to the font file (ensure the font is available)
                    output_image_path = f"output_{filename}"

                    # Add text to background and upload to Google Drive
                    uploaded_image = text_on_background(text, filename, font_path, output_image_path)
                    upload_to_drive(uploaded_image, drive_service)

        except Exception as e:
            print(f'An error occurred while downloading {filename}: {e}')

# Function to wrap text into multiple lines if necessary
def wrap_text(draw, text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        # Check the width of the current line with the new word using textbbox
        test_line = current_line + word + " "
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]

        # If it fits, add the word to the current line
        if text_width <= max_width:
            current_line = test_line
        else:
            # If it doesn't fit, start a new line
            if current_line != "":
                lines.append(current_line.strip())
            current_line = word + " "

    # Add the last line
    if current_line != "":
        lines.append(current_line.strip())
    print(f"Lines to be drawn: {lines}") 
    return lines

# Function to convert text to image with background and shadow
def text_on_background(text, background_image_path, font_path, output_image_path='output_image.png', line_height=15, shadow_offset=(5, 5)):
    # Open the background image
    image = Image.open(background_image_path)

    # Convert the image to RGB mode if it's not already in RGB mode
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Get the dimensions of the original image
    image_width, image_height = image.size

    # Calculate the coordinates to crop the image to 1080x1920 (portrait size)
    left = (image_width - 1080) // 2
    top = (image_height - 1920) // 2
    right = (image_width + 1080) // 2
    bottom = (image_height + 1920) // 2

    # Crop the image to 1080x1920 (portrait size)
    cropped_image = image.crop((left, top, right, bottom))

    # Set up the drawing context for the cropped image
    draw = ImageDraw.Draw(cropped_image)

    # Define padding (50px top and bottom, 20px left and right)
    padding_top = 140
    padding_bottom = 70
    padding_left = 10
    padding_right = 190

    # Calculate the available width and height for the text
    available_width = cropped_image.width - padding_left - padding_right
    available_height = cropped_image.height - padding_top - padding_bottom

    # Start with an initial font size and decrease until the text fits
    font_size = 150  # Start with a large font size
    font = ImageFont.truetype(font_path, font_size)

    # Try different font sizes to fit the text within the available space
    while True:
        # Wrap the text into lines
        lines = wrap_text(draw, text, font, available_width)

        # Calculate the total height required for the text
        total_text_height = sum([draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines])

        # Add line height space between lines
        total_text_height += (len(lines) - 1) * line_height

        # If the text fits within the available space, break the loop
        if total_text_height <= available_height:
            break

        # Otherwise, decrease the font size
        font_size -= 1
        font = ImageFont.truetype(font_path, font_size)

    # Recalculate lines after adjusting the font size
    lines = wrap_text(draw, text, font, available_width)

    # Calculate the starting position to center the text vertically
    total_text_height = sum([draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines])
    total_text_height += (len(lines) - 1) * line_height  # Add the line height space
    position_y = (cropped_image.height - total_text_height) // 2

    # Calculate the horizontal position to center the text
    position_x = padding_left

    # Draw each line of text with shadow
    for line in lines:
        print(f"Drawing line: {line}")
        # Calculate the width of the current line of text using textbbox
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]

        # Center the text horizontally
        position_x = (cropped_image.width - text_width) // 2

        # Draw shadow first (shadow_offset is used to create shadow offset)
        shadow_position = (position_x + shadow_offset[0], position_y + shadow_offset[1])
        draw.text(shadow_position, line, fill=(50, 50, 50), font=font)  # Darker shadow for better visibility

        # Draw the actual text
        draw.text((position_x, position_y), line, fill=(255, 255, 255), font=font)  # White text for good contrast

        # Move the vertical position down for the next line, with added line height space
        position_y += draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] + line_height

    # Apply sharpening filter to the image after drawing text
    sharpened_image = cropped_image.filter(ImageFilter.SHARPEN)

    # Save the resulting image locally before uploading
    sharpened_image.save(output_image_path,'PNG')
    print(f"Image saved at: {output_image_path}")

    return output_image_path

# Function to upload the image back to Google Drive
def upload_to_drive(image_path, drive_service):

    try:
        if not os.path.exists(image_path):
            print(f"File '{image_path}' does not exist!")
            return
    except Exception as e:
        print(f"Path doesn't exits : {e}")
    # Create a MediaFileUpload object for the image
    media = MediaFileUpload(image_path, mimetype='image/png')

    # Create a file metadata
    file_metadata = {
        'name': os.path.basename(image_path),  # File name on Google Drive
    }

    # Upload the file to Google Drive
    try:
        file = drive_service.files().create(
            media_body=media,
            body=file_metadata,
            fields='id'
        ).execute()

        print(f"File uploaded successfully: {file['name']} (ID: {file['id']})")
    except HttpError as e:
        traceback.print_exc()
        print(f"An error occurred while uploading the file: {e}")

# Run the function to download files from Google Drive
if __name__ == '__main__':
    download_files()
