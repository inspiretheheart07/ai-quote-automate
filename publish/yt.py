
import os
import sys
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
try:
    import http.client as httplib
except ImportError:
    import httplib
import httplib2
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload 
from googleapiclient.errors import HttpError 
import http.client
import random
import time
from alerts.mail import sendMail


YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
CLIENT_SECRETS_FILE = "client_secrets.json"
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,
  http.client.IncompleteRead, http.client.ImproperConnectionState,
  http.client.CannotSendRequest, http.client.CannotSendHeader,
  http.client.ResponseNotReady, http.client.BadStatusLine)
MAX_RETRIES = 10

def initialize_upload(Vfile,Vtitle,Vdesc,Vtags) :
    yt = get_service(YOUTUBE_UPLOAD_SCOPE,YOUTUBE_API_SERVICE_NAME)

    body = dict(
        snippet=dict(
            title=Vtitle,
            description='Vdesc',
            tags=Vtags,
            categoryId=22
        ),
        status=dict(
            privacyStatus='public'
        )
    )
    
    insert_request = yt.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(Vfile, chunksize=-1, resumable=True)
    )
    resumable_upload(insert_request)



def resumable_upload(insert_request) :
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print("Video id '%s' was successfully uploaded." % response['id'])
                else:
                    sendMail(None,"The upload failed with an unexpected response : YT : 68" )
                    exit("The upload failed with an unexpected response: %s" % response)
        except HttpError as e:  # updated exception handling
            if e.resp.status in RETRIABLE_STATUS_CODES:
                sendMail(None,"A retriable HTTP error %d occurred:\n%s : YT : 72")
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                                     e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:  # updated exception handling
            sendMail(None,"A retriable error occurred: %s :  YT : 78")
            error = "A retriable error occurred: %s" % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)


def get_service(scope, service, secret=None): 
    print(f"Using {CLIENT_SECRETS_FILE}")
    if not CLIENT_SECRETS_FILE:
        return None
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=scope)
    storage = Storage("oauth.json")
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage)    
    if not credentials:
        return None
    http = httplib2.Http()
    try:
        http.redirect_codes = set(http.redirect_codes) - {308} # https://github.com/googleapis/google-api-python-client/issues/803
    except AttributeError:
        pass
    return build("youtube", "v3", http=credentials.authorize(http))