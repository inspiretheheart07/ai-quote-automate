import random
from actions.quote_generate import genererateQuoteEnglish
from actions.download_files import download_files
from actions.image_processing import text_on_background
from actions.video_creation import create_video_with_music
from publish.yt import initialize_upload
from publish.fb import fbUpload
from publish.insta import postInsta
from publish.threads import threadsPost
from alerts.mail import sendMail

DRIVE_SCOPE = ['https://www.googleapis.com/auth/drive']
YT_SCOPE = ["https://www.googleapis.com/auth/youtube.upload"]
music_file = f"{random.randint(1, 11)}.mp3"
files_to_download = [music_file, 'font.ttf', 'bg.png']



def run():
    quote_json = genererateQuoteEnglish()
    if quote_json:
        download_files(scopes=DRIVE_SCOPE,files_to_download=files_to_download)
        uploaded_image = text_on_background(quote_json["quote"] , 'bg.png', 'font.ttf', 'output_image.png')
        if uploaded_image:
            video_path = create_video_with_music(uploaded_image, music_file)
            if video_path:
                try:
                    initialize_upload("output_video.mp4", quote_json["title"], quote_json["description"], quote_json["tags"])
                except Exception as e:
                    print(e)
                    sendMail(None,"YT upload failed")
                try :
                    fbUpload(quote_json)
                except Exception as e:
                    print(e)
                    sendMail(None,"Facebook Upload failed")
                try :
                    postInsta(quote_json)
                except Exception as e:
                    print(e)
                    sendMail(None,"Instagram Upload failed")
                try :
                    threadsPost(quote_json)
                except Exception as e:
                    print(e)
                    sendMail(None,"Threads Upload failed")

if __name__ == "__main__":
    run()
