import google.generativeai as genai
import os

# Retrieve the API Key from the environment or GitHub secrets
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Configure the Google Generative AI model
genai.configure(api_key=GOOGLE_API_KEY)

# Generate the quote using Gemini 2.0 model
model = genai.GenerativeModel('models/gemini-2.0-flash')
response = model.generate_content('Generate me one inspiring, wise, and heart-touching quote from a famous person that motivates and brings hope to others.')

# Extract and print the quote
quote = response.text.split(' - ')[0]
print(quote)
