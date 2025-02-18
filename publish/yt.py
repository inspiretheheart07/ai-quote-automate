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
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

# Explicitly tell the underlying HTTP transport library not to retry, since we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

CLIENT_SECRETS_FILE = "client_secrets.json"

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
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the API Console
https://console.cloud.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def get_authenticated_service():
        # Directly use oauth.json for OAuth authentication
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                                   scope=YOUTUBE_UPLOAD_SCOPE,
                                   message=MISSING_CLIENT_SECRETS_MESSAGE)

    # Run OAuth flow without storage (no file-based saving)
    credentials = run_flow(flow, None, args)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                 http=credentials.authorize(httplib2.Http()))

def initialize_upload(file_path, title, description, category =22, keywords = 'just upload', privacy_status='public'):
    youtube = get_authenticated_service()
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
