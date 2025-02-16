from actions.authenticate import initialize_yt_service, authenticate
from googleapiclient.http import MediaFileUpload

def uploadYt(scope, file_path, title, description, category_id="22"):
    # Authenticate the user and get credentials
    creds = authenticate(scopes=scope)
    
    # Check if credentials are obtained
    if creds:
        # Initialize the YouTube service with credentials
        youtube = initialize_yt_service(scopes=scope, creds=creds)

        # Prepare the request body with video metadata
        request_body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["tag1", "tag2"],  # You can customize the tags
                "categoryId": category_id,  # You can change category ID
            },
            "status": {
                "privacyStatus": "public",  # Options: "private", "unlisted", "public"
            },
        }

        # Create a MediaFileUpload instance to upload the video
        media = MediaFileUpload(file_path, mimetype="video/mp4", resumable=True)

        # Make the upload request to YouTube
        upload_request = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media
        )

        # Handle the video upload process
        response = None
        while response is None:
            status, response = upload_request.next_chunk()

            if status:
                print(f"Uploading... {int(status.progress() * 100)}%")

        print(f"Upload Complete! Video ID: {response['id']}")
    
    else:
        print("Authentication failed. No credentials found.")
