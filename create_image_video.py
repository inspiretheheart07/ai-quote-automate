import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from PIL import Image, ImageDraw, ImageFont

# Google Drive settings
FILE_ID = os.getenv("1-MvD1EumX_yChVWGhH6k34AAAP6REDhc")  # Set this to your desired file ID to download if needed
DESTINATION_PATH = "edited_image.png"  # Path to save the edited image

# Text to add to the image
TEXT = "Sample Text"
TEXT_POSITION = (50, 50)  # Position of the text on the image
TEXT_COLOR = (255, 0, 0)  # Red color for the text
FONT_SIZE = 30

# Path to the original bg.png (in your repository folder)
original_image_path = "bg.png"

# Open the image using Pillow
image = Image.open(original_image_path)

# Prepare to draw on the image
draw = ImageDraw.Draw(image)

# Load a font (optional, use default if you don't have a specific font)
font = ImageFont.load_default()

# Add text to the image
draw.text(TEXT_POSITION, TEXT, fill=TEXT_COLOR, font=font)

# Save the edited image
image.save(DESTINATION_PATH)
print(f"Text added and image saved as {DESTINATION_PATH}")

# Authenticate with Google Cloud (already done via the workflow step)
service = build("drive", "v3", cache_discovery=False)

# Upload the modified image back to Google Drive
file_metadata = {
    "name": "edited_image.png",  # Name of the file in Drive
    "mimeType": "image/png"  # MIME type for PNG image
}

media = MediaFileUpload(DESTINATION_PATH, mimetype="image/png")

# Perform the upload
uploaded_file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()

print(f"Uploaded file with ID: {uploaded_file['id']}")
