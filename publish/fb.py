import os
import requests

FACEBOOK_API_VERSION = os.getenv("FACEBOOK_API_VERSION") 

# Function to get a long-lived access token from a short-lived token
def get_long_lived_access_token(app_id, app_secret, short_lived_token):
    url = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_lived_token
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        long_lived_token = data["access_token"]
        print(f"Long-lived access token: {long_lived_token}")
        return long_lived_token
    else:
        print(f"Error getting long-lived token: {response.text}")
        return None

# Function to initialize the upload session
def initialize_upload_session(page_id, page_access_token, file_size):
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
        return None, None

# Function to finalize the upload
def finalize_upload(video_id, page_access_token, file_size, video_file_path):
    upload_url = f'https://rupload.facebook.com/video-upload/{FACEBOOK_API_VERSION}/{video_id}'
    
    headers = {
        "Authorization": f"OAuth {page_access_token}",
        "offset": "0",  # For the first upload, offset is usually 0
        "file_size": str(file_size),  # File size in bytes
    }
    
    with open(video_file_path, "rb") as video_file:
        response = requests.post(upload_url, headers=headers, data=video_file)
    
    if response.status_code == 200:
        print("Upload finalized successfully!")
        return True
    else:
        print(f"Error finalizing upload: {response.text}")
        return False

# Function to publish the video (finish the upload and set the video state to PUBLISHED)
def publishReel(page_id, page_access_token, video_id, description):
    finish_url = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}/{page_id}/video_reels"
    params = {
        "access_token": page_access_token,
        "video_id": video_id,
        "upload_phase": "finish",
        "video_state": "PUBLISHED",  # Set the state to PUBLISHED
        "description": description,  # Custom description for the video
    }
    
    response = requests.post(finish_url, params=params)
    
    if response.status_code == 200:
        print("Video published successfully!")
        print("Response:", response.json())
    else:
        print(f"Failed to publish video. Status code: {response.status_code}")
        print("Response:", response.text)

# Main function for video upload
def fbUpload():
    # Your app credentials (replace with your actual credentials)
    app_id = os.getenv("FACEBOOK_APP_ID")
    app_secret =  os.getenv("FACEBOOK_APP_SECRET") 
    short_lived_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")  # Short-lived token


    # Convert the short-lived token to a long-lived token
    long_lived_token = get_long_lived_access_token(app_id, app_secret, short_lived_token)
    
    if long_lived_token:
        page_access_token = long_lived_token  # Use the new long-lived token

        # Example usage for uploading and publishing a video
        page_id = os.getenv("FACEBOOK_PAGE_ID")
        video_file_path = '6775423-hd_1080_1920_24fps.mp4.mp4'
        file_size = os.path.getsize(video_file_path)
        
        # Step 1: Initialize the upload session
        video_id, upload_url = initialize_upload_session(page_id, page_access_token, file_size)
        
        if video_id and upload_url:
            # Step 2: Finalize the upload
            upload_successful = finalize_upload(video_id, page_access_token, file_size, video_file_path)
            
            if upload_successful:
                # Step 3: Publish the video
                description = "What a beautiful day! #sunnyand72"
                publishReel(page_id, page_access_token, video_id, description)
    else:
        print("Unable to get or refresh the access token. Please check your credentials.")
