from actions.authenticate import  authenticateYt
from googleapiclient.http import MediaFileUpload

def uploadYt(scope, file_path, title, description, category_id="22"):
    request_body = {
        "snippet": {
            "categoryId": category_id,
            "title": "Uploaded from Python",
            "description": description,
            "tags": ["test","python", "api" ]
        },
        "status":{
            "privacyStatus": "private"
        }
    }
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=googleapiclient.http.MediaFileUpload(file_path, chunksize=-1, resumable=True)
    )

    response = None 

    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload {int(status.progress()*100)}%")

        print(f"Video uploaded with ID: {response['id']}")
