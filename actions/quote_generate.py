import google.generativeai as genai
from google.generativeai import types
from alerts.mail import sendMail
import json
import random
import os


# Retrieve the API Key from the environment
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

def genererateQuoteEnglish():
        # Check if the API key is set
    if GOOGLE_API_KEY is None:
        raise ValueError("GOOGLE_API_KEY environment variable not set.")
    
    # Configure the Google Generative AI model
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # Generate the quote using Gemini model (specify the model name)
    model = genai.GenerativeModel('models/gemini-pro')
    
    adjectives = [
        "powerful", "inspiring", "thoughtful", "uplifting", "motivational", "wise", "heartfelt",
        "transformative", "moving", "courageous", "resilient", "unbreakable", "hopeful", "empowering", 
        "encouraging", "life-changing", "invincible", "remarkable", "strengthening", "enduring", 
        "brave", "unwavering", "heroic", "fearless", "compassionate", "visionary", "groundbreaking", 
        "exhilarating", "soothing", "healing", "compelling", "rejuvenating", "steadfast", "persistent", 
        "undaunted", "incomparable", "invigorating", "graceful", "magnificent", "uplifting", "soul-stirring", 
        "energizing", "faith-filled", "soulful", "enlightening", "impactful", "life-affirming", "encouraging", 
        "joyful", "uplifting", "extraordinary", "radiant", "humbling"
    ]
    random_adjective = random.choice(adjectives)
    
    prompt = f"""
    Generate a JSON object with a unique and {random_adjective} quote, title, description, and tags. Use the following JSON schema:
    
    {{
        "quote": "A new and unique inspiring, wise, and heart-touching quote about resilience from a famous person that motivates and brings hope to others. (string)",
        "title": "A short title that captures the essence of the quote. (string)",
        "description": "A brief description (2-3 sentences) explaining the meaning and context of the quote. (string)",
        "tags": ["A list of 10-25 relevant tags, including keywords related to the quote's theme. (array of strings)"]
    }}
    
    Example:
    {{
        "quote": "The only way to do great work is to love what you do. - Steve Jobs",
        "title": "Passion for Work",
        "description": "This quote emphasizes the importance of finding passion in your work. It suggests that genuine fulfillment and excellence come from pursuing what you truly love.",
        "tags": ["passion", "work", "motivation", "inspiration", "success"]
    }}
    
    Return only the JSON object. Do not include any extra text. Generate a new and unique quote each time.
    """
    
    try:
        response = model.generate_content(prompt, generation_config=types.GenerationConfig(
            max_output_tokens=500,
            temperature=0.7
        ))
    
        if not response.text:
            print("Error: Gemini model returned an empty response.")
            print("Raw Response:", response)
            sendMail(None,"Error: Gemini model returned an empty response : generateQuoteEnglish : 72")
            raise ValueError("Empty response from Gemini model.")
    
        data = json.loads(response.text)
    
        # Validate the JSON data
        if isinstance(data, dict) and "quote" in data and "title" in data and "description" in data and "tags" in data and isinstance(data["tags"], list):
            quote = data["quote"]
            title = data["title"]
            description = data["description"]
            tags = data["tags"]
    
            # Extract the author from the quote
            author = None
            if "-" in quote:
                quote_parts = quote.split("-")
                quote = quote_parts[0].strip()
                author = quote_parts[1].strip()
    
            # Generate the new title
            if author:
                new_title = f"{quote} by {title} - {author}"
            else:
                new_title = f"{quote} by {title}"
    
            print(f"Quote: {quote}")
            print(f"New Title: {new_title}")
            print(f"description: {description}")
            print(f"tags: {tags}")
    
            with open("quote_data.json", "w", encoding="utf-8") as f:
                data["quote"] = quote
                data["title"] = new_title
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("Quote data saved to quote_data.json")
            return data
        else:
            print("Invalid JSON structure.")
            print("Response Text:", response.text)
            sendMail(None,"Invalid JSON structure : generateQuoteEnglish : 111")
    
    except json.JSONDecodeError as e:
        print(f"Error: Could not parse JSON response. Error: {e} : generateQuoteEnglish : 114")
        sendMail(None,e)
    except AttributeError:
        print("Error: Could not extract quote from response. Check the model output.")
        sendMail(None,'Error: Could not extract quote from response. Check the model output. : generateQuoteEnglish : 118')
    except ValueError as ve:
        print(f"ValueError: {ve}")
        sendMail(None,f"{ve} : generateQuoteEnglish : 121")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sendMail(None,f"An unexpected error occurred: {e} : generateQuoteEnglish : 123")