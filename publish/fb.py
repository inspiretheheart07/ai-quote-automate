import os
import requests
from alerts.mail import sendMail

def initialize_upload_session(page_id, page_access_token, file_size):
    """
    Initialize the upload session for resumable upload.
    """
    url = f'https://graph.facebook.com/{FACEBOOK_API_VERSION}/{page_id}/video_reels'
    params = {
        'upload_phase': 'start',
        'access_token': page_access_token,
        'file_size': file_size
    }
    
    response = requests.post(url, params=params)
    if response.status_code == 200:
        data = response.json()
        video_id = data['video_id']
        upload_url = data['upload_url']
        print(f"Upload session initialized: video_id={video_id}, upload_url={upload_url}")
        return video_id, upload_url
    else:
        print(f"Error initializing upload session: {response.text}")
        sendMail(None,f"Error initializing upload session: {response.text} : Facebook : 25")


def finalize_upload(page_id, page_access_token, video_id, video_file_path):
    """
    Finalize the upload session.
    """
    upload_url = f'https://rupload.facebook.com/video-upload/{FACEBOOK_API_VERSION}/{video_id}'
    file_size = os.stat(video_file_path).st_size
    # Headers
    headers = {
        "Authorization": f"OAuth {page_access_token}",
        "offset": "0",  # For the first upload, offset is usually 0
        "file_size": str(file_size),  # File size in bytes
    }
    
    # Open and upload the file using the `data-binary` equivalent in requests
    with open(video_file_path, "rb") as video_file:
        response = requests.post(upload_url, headers=headers, data=video_file)
    if response.status_code == 200:
        print("Upload finalized successfully!")
        return True
    else:
        print(f"Error finalizing upload: {response.text}")
        sendMail(None,f"Error finalizing upload: {response.text} : Facebook  : 51")
        return False
    
def publishReel(page_id, page_access_token, video_id,quote_data):
    finish_url = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}/{page_id}/video_reels"
    params = {
    "access_token": page_access_token,
    "video_id": video_id,
    "upload_phase": "finish",
    "video_state": "PUBLISHED",  # You can set the state to PUBLISHED
    "description": f"✨ {quote_data['title']} ✨\n\n{quote_data['quote']}\n\n{quote_data['description']}\n\n#{' #'.join(quote_data['tags'])}\n#Inspiration #Motivation",  # Your custom description for the video
    }
    
    # Send the POST request to finish the upload and publish the video
    response = requests.post(finish_url, params=params)
    
    # Check the response
    if response.status_code == 200:
        print("Video published successfully!")
    else:
        print(f"Failed to publish video. Status code: {response.status_code}")
        print("Response:", response.text)
        sendMail(None,f"Failed to publish video. Status code: {response.status_code} : Facebook : 74")


# Example usage
page_id = os.getenv("FACEBOOK_PAGE_ID")
page_access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")

FACEBOOK_API_VERSION = os.getenv("FACEBOOK_API_VERSION") 


def fbUpload(quote):
    video_file_path = 'output_video.mp4'
    file_size = os.path.getsize(video_file_path)
    # Step 1: Initialize the upload session
    video_id, upload_url = initialize_upload_session(page_id, page_access_token, file_size)
    if video_id and upload_url:
       upload =  finalize_upload(page_id, page_access_token, video_id, video_file_path)
       if upload:
           publishReel(page_id, page_access_token, video_id,quote)
    