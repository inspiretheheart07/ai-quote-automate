import requests
import os
from alerts.mail import sendMail

instagram_account_id = os.getenv("INSTA_PAGE_ID")  # Replace with your valid Instagram account ID
VERSION = os.getenv("FACEBOOK_API_VERSION")
graph_url = f'https://graph.facebook.com/{VERSION}/'

def post_reel(caption='', media_type='', share_to_feed='TRUE', thumb_offset='0', video_url='', access_token='', instagram_account_id=instagram_account_id):
    """
    Function to upload a reel (video) to Instagram.
    """
    url = f'{graph_url}{instagram_account_id}/media'  # URL to upload media
    param = dict()

    # Required parameters
    param['access_token'] = access_token
    param['media_type'] = media_type  # 'VIDEO' or 'IMAGE'
    param['upload_type']='resumable'
    param['caption']=caption
    param['thumb_offset']='0'


    response = requests.post(url, params=param)
    
    if response.status_code == 200:
        print("Upload started successfully.")
        response_json = response.json()
        print(response_json)
        return response_json  # Returns response JSON with the creation ID
    else:
        print(f"Error uploading media: {response.status_code}")
        print(response.content)
        sendMail(None,f"Error uploading media: {response.status_code} : Instagram : 34")
        return None


def finalize_upload(page_id, page_access_token, video_id, video_file_path):
    """
    Finalize the upload session.
    """
    upload_url = f'https://rupload.facebook.com/ig-api-upload/{VERSION}/{video_id}'
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
        sendMail(None,f"Error finalizing upload: {response.text} : Instagram : 61")
        return False
    

def publish_container(creation_id='', access_token='', instagram_account_id=''):
    """
    Function to publish the uploaded media after checking its status.
    """
    # Construct URL for publishing the media
    url = f'https://graph.facebook.com/{VERSION}/{instagram_account_id}/media_publish?access_token={access_token}'

    # You can add headers if necessary (mimicking the curl headers)
    params = {
        'creation_id':{creation_id},
       
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
     }

    # Send the POST request to publish the media
    response = requests.post(url, data=params,headers=headers)

    if response.status_code == 200:
        print("Media published successfully.")
        return response.json()  # Return the publish response
    else:
        print(f"Error publishing media: {response.status_code}")
        print(response.content)  # Print detailed response content for debugging
        sendMail(None,f"Error publishing media: {response.status_code} : Instagram : 91")
        return None


# Example usage
access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
media_type = 'REELS'  # 'VIDEO' for video posts
video_url = 'output_video.mp4'  # Replace with your valid video URL

def postInsta(quote_data) :
    caption = f"✨ {quote_data['title']} ✨\n\n{quote_data['quote']}\n\n{quote_data['description']}\n\n#{' #'.join(quote_data['tags'])}\n#Inspiration #Motivation"
        # Step 1: Post the reel (video)
    response = post_reel(caption=caption, media_type=media_type, video_url=video_url, access_token=access_token,instagram_account_id=instagram_account_id)
    
    if response:
        creation_id = response['id']  # Get the creation ID (container ID) from the response
        print(f"Media container created with ID: {creation_id}")
        
        # Step 2: Check upload status using the while loop
        upload_status = finalize_upload('' ,access_token,creation_id,r'output_video.mp4')
        print("Upload Status:", upload_status)
    
        # Step 3: If upload is finished, publish the media
        if upload_status :
            publish_response = publish_container(creation_id, access_token,instagram_account_id)
            print("Publish to Insta sucessfull")
    else:
        print("Failed to upload the media.")
        sendMail(None,"Insta upload Failed")
