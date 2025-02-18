import os
import random
import time
import http.client
import httplib2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.auth import exceptions, impersonated_credentials
from google.oauth2 import service_account

# Explicitly tell the underlying HTTP transport library not to retry, since we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (
    httplib2.HttpLib2Error, IOError, http.client.NotConnected,
    http.client.IncompleteRead, http.client.ImproperConnectionState,
    http.client.CannotSendRequest, http.client.CannotSendHeader,
    http.client.ResponseNotReady, http.client.BadStatusLine
)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# Define constants
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

def get_authenticated_service():
    """Authenticate and create a YouTube API service client."""
    # Load the service account credentials
    credentials = service_account.Credentials.from_service_account_file(
        'oauth.json', scopes=[YOUTUBE_UPLOAD_SCOPE])

    # Build and return the API service client
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentials)
    return youtube

def initialize_upload(youtube, file_path, title, description, category, keywords, privacy_status):
    """Upload the video to YouTube."""
    tags = keywords.split(",") if keywords else None

    body = dict(
        snippet=dict(
            title=title,
            description=description,
            tags=tags,
            categoryId=category
        ),
        status=dict(
            privacyStatus=privacy_status
        )
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
    )

    resumable_upload(insert_request)

def resumable_upload(insert_request):
    """Handles the upload with exponential backoff in case of failures."""
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print(f"Video id '{response['id']}' was successfully uploaded.")
                else:
                    exit(f"The upload failed with an unexpected response: {response}")
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = f"A retriable error occurred: {e}"

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print(f"Sleeping {sleep_seconds} seconds and then retrying...")
            time.sleep(sleep_seconds)

if __name__ == '__main__':
    # Get parameters from environment variables
    file_path = os.getenv("FILE_PATH")
    title = os.getenv("TITLE", "Test Title")
    description = os.getenv("DESCRIPTION", "Test Description")
    category = os.getenv("CATEGORY", "22")
    keywords = os.getenv("KEYWORDS", "")
    privacy_status = os.getenv("PRIVACY_STATUS", "public")

    if not file_path:
        exit("Please specify a valid file path.")

    youtube = get_authenticated_service()
    try:
        initialize_upload(youtube, file_path, title, description, category, keywords, privacy_status)
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
