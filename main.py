from actions.download_files import download_files
from actions.image_processing import text_on_background
from actions.video_creation import create_video_with_music


def run():
    # Custom scopes if needed, else defaults to Google Drive access
    custom_scopes = ['https://www.googleapis.com/auth/drive.file']
    download_files(scopes=custom_scopes)

    # Example usage of text and background image creation
    text = "Your Custom Text Here"
    uploaded_image = text_on_background(text, 'bg.png', 'font.ttf', 'output_image.png')
    if uploaded_image:
        video_path = create_video_with_music(uploaded_image, f"{random.randint(1, 11)}.mp3")
        if video_path:
            upload_to_drive(video_path)

if __name__ == "__main__":
    run()
