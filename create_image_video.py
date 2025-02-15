from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.auth import default
from PIL import Image, ImageDraw, ImageFont
import os

# Function to search for file by name on Google Drive and get file ID
def search_file_id(service, file_name):
    results = service.files().list(
        q=f"name='{file_name}'", fields="files(id, name)").execute()
    files = results.get('files', [])
    
    if not files:
        print(f"No files found with the name: {file_name}")
        return None

    return files[0]['id']  # Return the first match's ID

# Function to download file from Google Drive
def download_file(service, file_id, destination):
    request = service.files().get_media(fileId=file_id)
    with open(destination, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")
    print(f"Downloaded {destination}.")

# Function to upload file to Google Drive
def upload_file(service, file_path, file_metadata, mimetype='image/png'):
    media = MediaFileUpload(file_path, mimetype=mimetype)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"File uploaded to Drive with ID: {file['id']}.")

# Main execution
def main():
    # Get authenticated credentials
    creds, _ = default(scopes=["https://www.googleapis.com/auth/drive.readwrite"])

    # Build the Drive API client
    drive_service = build('drive', 'v3', credentials=creds)

    # Search for the files by name
    bg_image_id = search_file_id(drive_service, 'bg.png')
    font_id = search_file_id(drive_service, 'font.ttf')

    if not bg_image_id or not font_id:
        print("Error: Could not find the required files on Google Drive.")
        return

    # Folder ID to upload the generated image
    folder_id = '1-MvD1EumX_yChVWGhH6k34AAAP6REDhc'  # Replace with your folder ID

    # Paths to download the files
    bg_image_path = '/tmp/bg.png'
    font_path = '/tmp/font.ttf'
    output_image_path = '/tmp/output_image.png'

    # Download the background image and font file
    download_file(drive_service, bg_image_id, bg_image_path)
    download_file(drive_service, font_id, font_path)

    # Get the quote from environment variable
    quote = os.getenv("QUOTE", "Default quote")

    # Open the background image and font
    img = Image.open(bg_image_path)
    draw = ImageDraw.Draw(img)

    # Set up the font (adjust size as needed)
    font = ImageFont.truetype(font_path, 30)

    # Define the position for the quote text
    text_width, text_height = draw.textsize(quote, font=font)
    width, height = img.size
    x_pos = (width - text_width) // 2  # Center horizontally
    y_pos = height // 2 - text_height // 2  # Center vertically

    # Add the quote text to the image
    draw.text((x_pos, y_pos), quote, font=font, fill="white")

    # Save the output image
    img.save(output_image_path)
    print(f"Image saved to {output_image_path}.")

    # Upload the generated image back to Google Drive
    file_metadata = {
        'name': 'output_image.png',
        'parents': [folder_id]  # Upload to the specified folder
    }
    upload_file(drive_service, output_image_path, file_metadata)

if __name__ == "__main__":
    main()
