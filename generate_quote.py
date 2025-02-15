import os
import google.generativeai as genai

# Retrieve GOOGLE_API_KEY from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY is None:
    raise ValueError("GOOGLE_API_KEY environment variable is missing.")

# Configure the API key for Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)

# Create a GenerativeModel instance with the model name
model = genai.GenerativeModel('models/gemini-2.0-flash')

# Generate content
response = model.generate_content("Generate me one inspiring, wise, and heart-touching quote from a famous person that motivates and brings hope to others.")

# Extract and print the quote
quote = response.text.split(' - ')[0]
print(quote)

# Save the quote to a file to pass it to the next Python script
with open("quote.txt", "w") as f:
    f.write(quote)