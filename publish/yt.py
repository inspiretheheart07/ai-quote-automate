
import os
import sys
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
CLIENT_SECRETS_FILE = "client_secrets.json"

                

def initialize_upload(Vfile,Vtitle,Vdesc) :
    print(get_service(YOUTUBE_UPLOAD_SCOPE,YOUTUBE_API_SERVICE_NAME))

def get_service(scope, service, secret=None): 

    print(f"Using {CLIENT_SECRETS_FILE}")

    if not CLIENT_SECRETS_FILE:
        return None

    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=scope)

    # flow.user_agent = consts.long_name
    storage = Storage("oauth.json")
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage)

    return credentials