
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