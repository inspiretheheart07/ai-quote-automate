import os
import requests
import base64
import json
from datetime import datetime, timedelta, timezone
import time

# Facebook App details (for token exchange)
facebook_app_id = os.getenv("FACEBOOK_APP_ID")  # Your Facebook App ID
facebook_app_secret = os.getenv("FACEBOOK_APP_SECRET")  # Your Facebook App Secret

FACEBOOK_API_VERSION = os.getenv("FACEBOOK_API_VERSION") 

# Facebook Page ID
facebook_page_id = os.getenv("FACEBOOK_PAGE_ID")

def decode_jwt(token):
    """Decode the JWT token and extract the expiration time."""
    # Split the token into header, payload, and signature
    token_parts = token.split('.')
    
    if len(token_parts) != 3:
        print("Invalid token format.")
        return None
    
    # Decode the payload (second part) from base64
    payload = base64.b64decode(token_parts[1] + "==")  # Add padding if necessary
    
    # Convert the payload to a dictionary
    payload_data = json.loads(payload)
    
    # Get the expiration time (exp field)
    exp_timestamp = payload_data.get('exp')
    
    if exp_timestamp:
        # Convert the expiration time to a readable datetime format
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        return exp_datetime
    else:
        print("Expiration field not found in the token.")
        return None

def refresh_facebook_token(long_lived_token):
    """Refresh the long-lived token using the long-lived token."""
    
    url = f'https://graph.facebook.com/{FACEBOOK_API_VERSION}/oauth/access_token'
    
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': facebook_app_id,
        'client_secret': facebook_app_secret,
        'fb_exchange_token': long_lived_token
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'access_token' in data:
        print("Token refreshed successfully.")
        return data['access_token']
    else:
        print(f"Error refreshing token: {data}")
        return None

def upload_video_to_facebook(page_access_token, video_path, caption, page_id):
    """Upload video to Facebook."""
    url = f'https://graph-video.facebook.com/{FACEBOOK_API_VERSION}/{page_id}/videos'
    
    params = {
        'access_token': page_access_token,
        'description': caption
    }
    
    files = {
        'file': open(video_path, 'rb')
    }
    
    response = requests.post(url, params=params, files=files)
    
    if response.status_code == 200:
        print("Video uploaded successfully to Facebook.")
    else:
        print(f"Error uploading video: {response.text}")

def uploadToFb(video_file,caption):
   # Facebook Page access token (your long-lived token)
    facebook_page_access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")  # Your long-lived token

    # Upload video to Facebook (always uses the latest token)
    upload_video_to_facebook(facebook_page_access_token, video_file, caption, facebook_page_id)

    # Refresh the token
    facebook_page_access_token = refresh_facebook_token(facebook_page_access_token)
