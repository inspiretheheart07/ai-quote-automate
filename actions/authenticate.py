import json
import os
import google_auth_oauthlib.flow
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

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

def authenticateYt(scopes=None):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"    
    service_account_json = os.getenv('GOOGLE_YT_API_KEY')
    if not service_account_json:
        raise ValueError("Service account credentials JSON is not set.")    
    # Write the service account JSON to a temporary file
    with open('client_secrets.json', 'w') as json_file:
        json_file.write(service_account_json)    
    # Use the file path for `from_client_secrets_file`
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json', scopes)    
    credentials = flow.run_local_server(port=0)
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", credentials=credentials)

    return youtube


def authenticateAnother(scopes=None):
    creds = None
    service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
    if not service_account_json:
        raise ValueError("Service account credentials JSON is not set.")
    
    credentials_data = json.loads(service_account_json)
    if scopes is None:
        print(f"::::::::::::::: No Scope Provided :::::::::::::::")
        return

    creds = service_account.Credentials.from_service_account_info(credentials_data, scopes=scopes)
    youtube = build('youtube', 'v3', credentials=creds)
    return youtube




def authenticateYtTest(scopes=None):
    creds = None
    # Token file to store the user's access and refresh tokens
    token_file = 'token.pickle'
    
    # If there are already valid credentials, load them from token.pickle
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            service_account_json = os.getenv('GOOGLE_YT_API_KEY')
            if not service_account_json:
                raise ValueError("Service account credentials JSON is not set.")    
                # Write the service account JSON to a temporary file
            with open('client_secrets.json', 'w') as json_file:
                json_file.write(service_account_json) 
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', scopes)
            creds = flow.run_console()  # This will run in the console, no browser
        # Save the credentials for the next run
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    # Build the YouTube API client
    youtube = build('youtube', 'v3', credentials=creds)
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