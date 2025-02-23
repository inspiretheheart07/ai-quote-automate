import requests
import time
import os
from alerts.mail import sendMail
from amazons3.upload import upload_file_to_s3


threads_account_id = os.getenv("THREADS_PAGE_ID")
THREAD_VERSION = os.getenv("THREAD_VERSION")
graph_url = f'https://graph.threads.net/{THREAD_VERSION}/'

def post_reel(caption='', media_type='', video_url='', access_token='', threads_account_id=threads_account_id):
    """
    Function to upload a reel (video) to Instagram.
    """
    url = f'{graph_url}{threads_account_id}/threads'  # URL to upload media
    param = dict()

    # Required parameters
    param['access_token'] = access_token
    param['media_type'] = media_type 
    param['video_url'] = video_url
    param['text'] = caption  # 'text' key for caption


    response = requests.post(url, params=param)
    print(url, response.json())
    if response.status_code == 200:
        print("Upload started successfully.")
        response_json = response.json()
        return response_json  # Returns response JSON with the creation ID
    else:
        print(f"Error uploading media: {response.status_code}")
        print(response.content)
        sendMail(None,f"Error uploading media: {response.status_code} : Threads : 33")
        return None


def check_upload_status(creation_id, access_token, threads_account_id):
    """
    Function to check the status of the uploaded media.
    """
    url = f'{graph_url}{creation_id}?access_token={access_token}'
    
    response = requests.get(url)
    print(url, response.json())
    
    if response.status_code == 200:
        status_data = response.json()
        status = status_data.get("status")
        if status == "ERROR" :
            print("Media Failed")
            sendMail(None,"uploaded media Failed : Threads 51")
            return status
        elif status == "FINISHED":  # The media is ready to be published
            print("Media is ready to be published.")
            return status
        else:
            print("Media still processing...")
            return status
    else:
        print(f"Error checking upload status: {response.status_code}")
        print(response.content)
        return False


def publish_container(creation_id, access_token, threads_account_id):
    """
    Function to publish the uploaded media after checking its status.
    """
    # Construct URL for publishing the media
    url = f'{graph_url}{threads_account_id}/threads_publish?access_token={access_token}&creation_id={creation_id}'

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    # Send the POST request to publish the media
    response = requests.post(url, headers=headers)
    print(url, response.json())
    if response.status_code == 200:
        print("Media published successfully.")
        return response.json()  # Return the publish response
    else:
        print(f"Error publishing media: {response.status_code}")
        print(response.content)  # Print detailed response content for debugging
        sendMail(None,f"Error publishing media: {response.status_code} : Threads : 85")
        return None


# Example usage
access_token = os.getenv("THREADS_TOKEN")  # Replace with your valid access token
media_type = 'VIDEO'  # 'VIDEO' for video posts

def threadsPost(quote_data):
    video_url = upload_upload_file_to_s3file()
    # Step 1: Post the reel (video)
    caption = f"✨ {quote_data['title']} ✨\n\n{quote_data['quote']}\n\n{quote_data['description']}\n\n#{' #'.join(quote_data['tags'])}\n#Inspiration #Motivation"
    response = post_reel(caption=caption, media_type=media_type, video_url=video_url, access_token=access_token,threads_account_id=threads_account_id)
    
    if response:
        creation_id = response['id']  # Get the creation ID (container ID) from the response
        print(f"Media container created with ID: {creation_id}")
        
        # Step 2: Check the upload status until it is ready
        while  check_upload_status(creation_id, access_token, threads_account_id) == "IN_PROGRESS" :
            print("Waiting for media to be processed...")
            time.sleep(5)  # Wait 30 seconds before checking the status again
            if check_upload_status(creation_id, access_token, threads_account_id) == "FINISHED" :
                # Step 3: Publish the media after it's ready
                publish_response = publish_container(creation_id, access_token, threads_account_id)
                print("Published to threads Sucessfully")
                # delete_file()
            else:
                sendMail(None,"Failed to upload to Threads : Threads : 112")
                print("Failed to upload")
                # delete_file()
    else:
        sendMail(None,"Failed to upload to Threads : 115")
        print("Failed to upload the media.")
        # delete_file()
    