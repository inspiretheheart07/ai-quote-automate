import json
import os
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def authenticate(scopes=None):
    creds = None
    service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
    if not service_account_json:
        raise ValueError("Service account credentials JSON is not set.")
    
    credentials_data = json.loads(service_account_json)
    if scopes is None:
        print(f"::::::::::::::: No Scope Provided :::::::::::::::")
        return

    creds = service_account.Credentials.from_service_account_info(credentials_data, scopes=scopes)
    return creds

import os
import json
import google_auth_oauthlib.flow
import googleapiclient.discovery

TOKEN_FILE = 'token.json'  # Define your token file path
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']  # Adjust this based on the API scope you need

def authenticateYt(scopes=None):
    scopes = scopes or SCOPES
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
    service_account_json = os.getenv('GOOGLE_YT_API_KEY')
    if not service_account_json:
        raise ValueError("Service account credentials JSON is not set.")
    client_secrets_file = json.loads(service_account_json)
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_local_server()
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", credentials=credentials)

    return youtube


def initialize_drive_service(scopes=None,creds=None):
    if scopes is None:
        print(f"::::::::::::::: No Scope Provided :::::::::::::::")
        return
    if creds is None:
        print(f"::::::::::::::: No creds Provided :::::::::::::::")
        return
    return build('drive', 'v3', credentials=creds)

def initialize_yt_service(scopes=None,creds=None):
    if scopes is None:
        print(f"::::::::::::::: No Scope Provided :::::::::::::::")
        return
    if creds is None:
        print(f"::::::::::::::: No creds Provided :::::::::::::::")
        return
    return build('youtube', 'v3', credentials=creds)