import random

from actions.download_files import download_files
from actions.image_processing import text_on_background
from actions.video_creation import create_video_with_music

DRIVE_SCOPE = ['https://www.googleapis.com/auth/drive']
music_file = f"{random.randint(1, 11)}.mp3"
files_to_download = [music_file, 'font.ttf', 'bg.png']

def run():
    download_files(scopes=DRIVE_SCOPE,files_to_download=files_to_download)
    text = "Your Custom Text Here"
    uploaded_image = text_on_background(text, 'bg.png', 'font.ttf', 'output_image.png')
    if uploaded_image:
        video_path = create_video_with_music(uploaded_image, music_file)
if __name__ == "__main__":
    run()
