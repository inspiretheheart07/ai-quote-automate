import json
import os
from google.oauth2 import service_account
from google.auth.transport.requests import Request

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

def initialize_drive_service(scopes=None,creds=None):
    if scopes is None:
        print(f"::::::::::::::: No Scope Provided :::::::::::::::")
        return
    if creds is None:
        print(f"::::::::::::::: No creds Provided :::::::::::::::")
        return
    return build('drive', 'v3', credentials=creds)