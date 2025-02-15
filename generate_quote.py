import os
from google.generativeai import Client

# The GOOGLE_APPLICATION_CREDENTIALS environment variable is automatically set by the GitHub Action
# client = Client()  # No need to explicitly pass credentials if the env var is set

# It is better to create the client with the credentials file path
credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
client = Client(credentials_file=credentials_path)

response = client.generate_text(
    model="text-bison-001",  # Replace with your desired model
    prompt="Generate me one inspiring, wise, and heart-touching quote from a famous person that motivates and brings hope to others."
)

print(response.result)
