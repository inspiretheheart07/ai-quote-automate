import os
import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload

def uploadYt(vFile,vTitle,Vdesc):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = os.getenv('GOOGLE_YT_API_KEY')

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.videos().insert(
        part="snippet,status",
        body={
          "snippet": {
            "categoryId": "22",
            "description": Vdesc,
            "title": vTitle
          },
          "status": {
            "privacyStatus": "private"
          }
        },
        media_body=MediaFileUpload(vFile)
    )
    response = request.execute()

    print(response)