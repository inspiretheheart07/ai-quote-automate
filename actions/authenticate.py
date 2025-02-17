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

def authenticateYt(scopes=None):
    scopes = scopes
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"    
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)    
    service_account_json = os.getenv('GOOGLE_YT_API_KEY')
    if not service_account_json:
        raise ValueError("Service account credentials JSON is not set.")    
    # Write the service account JSON to a temporary file
    with open('client_secrets.json', 'w') as json_file:
        json_file.write(service_account_json)    
    # Use the file path for `from_client_secrets_file`
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json', scopes)    
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