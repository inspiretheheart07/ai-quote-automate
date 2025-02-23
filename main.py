import random
from actions.quote_generate import genererateQuoteEnglish
from actions.download_files import download_files
from actions.image_processing import text_on_background
from actions.video_creation import create_video_with_music
from publish.yt import initialize_upload
from publish.fb import fbUpload
from publish.insta import postInsta
from publish.threads import threadsPost
import asyncio

DRIVE_SCOPE = ['https://www.googleapis.com/auth/drive']
YT_SCOPE = ["https://www.googleapis.com/auth/youtube.upload"]
music_file = f"{random.randint(1, 11)}.mp3"
files_to_download = [music_file, 'font.ttf', 'bg.png']


async def upload_to_platforms(quote_json, video_path):
    # Initialize all upload functions to run concurrently
    tasks = [
        asyncio.to_thread(initialize_upload("output_video.mp4", quote_json["title"], quote_json["description"], quote_json["tags"])),
        asyncio.to_thread(fbUpload(quote_json)),
        asyncio.to_thread(postInsta(quote_json)),
        asyncio.to_thread(threadsPost(quote_json))
    ]
    await asyncio.gather(*tasks)


def run():
    quote_json = genererateQuoteEnglish()
    if quote_json:
        download_files(scopes=DRIVE_SCOPE,files_to_download=files_to_download)
        uploaded_image = text_on_background(quote_json["quote"] , 'bg.png', 'font.ttf', 'output_image.png')
        if uploaded_image:
            video_path = create_video_with_music(uploaded_image, music_file)
            if video_path:
                asyncio.run(upload_to_platforms(quote_json, video_path))

if __name__ == "__main__":
    run()
