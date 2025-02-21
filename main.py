import random

from actions.download_files import download_files
from actions.image_processing import text_on_background
from actions.video_creation import create_video_with_music
from publish.yt import initialize_upload
from publish.fb import fbUpload

DRIVE_SCOPE = ['https://www.googleapis.com/auth/drive']
YT_SCOPE = ["https://www.googleapis.com/auth/youtube.upload"]
music_file = f"{random.randint(1, 11)}.mp3"
files_to_download = [music_file, 'font.ttf', 'bg.png']

def run():
    download_files(scopes=DRIVE_SCOPE,files_to_download=files_to_download)
    text = "Your Custom Text Here"
    uploaded_image = text_on_background(text, 'bg.png', 'font.ttf', 'output_image.png')
    if uploaded_image:
        video_path = create_video_with_music(uploaded_image, music_file)
        print(f"::::::::::::::: Video Created Success :::::::::::::::")
        if video_path:
            print(f"::::::::::::::: Video Upload Started :::::::::::::::")
            # initialize_upload("output_video.mp4", "Video Title", "Description")
            fbUpload()

if __name__ == "__main__":
    run()
