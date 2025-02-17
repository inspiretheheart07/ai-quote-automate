from actions.authenticate import authenticateAnother
from googleapiclient.http import MediaFileUpload

def uploadYt(scope, file_path, title, description, category_id="22"):
    youtube = authenticateAnother(scope)
    request_body = {
        "snippet": {
            "categoryId": category_id,
            "title": title,
            "description": description,
            "tags": ["test", "python", "api"]
        },
        "status": {
            "privacyStatus": "private"
        }
    }
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload {int(status.progress()*100)}%")

    print(f"Video uploaded with ID: {response['id']}")
