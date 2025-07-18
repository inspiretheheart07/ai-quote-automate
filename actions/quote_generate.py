import google.generativeai as genai
from google.generativeai import types
from alerts.mail import sendMail
import json
import random
import os


# Retrieve the API Key from the environment
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GCP_PR_NAME = os.getenv('GCP_PROJECT_NAME')

def genererateQuoteEnglish():
        # Check if the API key is set
    if GOOGLE_API_KEY is None:
        raise ValueError("GOOGLE_API_KEY environment variable not set.")
    
    # Configure the Google Generative AI model
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # Generate the quote using Gemini model (specify the model name)
    model = genai.GenerativeModel(GCP_PR_NAME)
        
    adjectives = [
        "sad","broken","unhappy", "sorrowful", "melancholy", "downcast", "mournful", "grief-stricken", "depressed", "blue", "heartbroken", "despondent", 
  "disheartened", "woeful", "downhearted", "forlorn", "dismal", "glum", "gloomy", "tearful", "desolate", "lamenting", 
  "woeful", "miserable", "crushed", "inconsolable", "heavy-hearted", "bereaved", "anguished", "wistful", "miserable", "lost", 
  "sorrowful", "brokenhearted", "pensive", "troubled", "aching", "low-spirited", "bleak", "shaken", "devastated", "afflicted", 
  "despairing", "regretful", "dismal", "troubled", "helpless", "broken", "bitter", "humiliated", "discouraged", "frustrated", 
  "teary-eyed", "discouraged", "dejected", "somber", "teary", "numb", "melancholic", "pain-stricken", "disillusioned", "down", 
  "discontented", "hopeless", "inconsolable", "forlorn", "anguished", "heart-sick", "broken-spirited", "lamenting", "weary", 
  "sick-at-heart", "hurt", "downcast", "gloomy", "aching", "distressed", "overwhelmed", "tortured", "weeping", "discouraged", 
  "deflated", "lonely", "withdrawn", "despondent", "hopeless", "mournful", "troubled", "disheartened", "miserable", "downtrodden", 
  "grief-filled", "troubled", "sad-eyed", "despair-stricken", "shattered", "cracked", "fractured", "damaged", "battered", 
  "ruined", "destroyed", "defeated", "splintered", "crumbled", "torn", "wounded", "disrupted", "collapsed", "dismantled", 
  "depleted", "fragmented", "in pieces", "hurt", "shattered", "torn apart", "disintegrated", "undone", "incapacitated", "disordered", 
  "ruined", "invalidated", "impaired", "split", "cracked", "collapsed", "fractured", "crushed", "defeated", "disarranged", "disheveled", 
  "obliterated", "brokenhearted", "shattered", "wrecked", "faltering", "disconnected", "malfunctioning", "damaged", "disassembled", 
  "ruined", "mutilated", "lost", "exhausted", "wrecked", "defaced", "fragmented", "inoperative", "weak", "impaired", "unhinged", 
  "undone", "crushed", "broken down", "bent", "incapacitated", "crippled", "torn to pieces", "battered", "useless", "incomplete", 
  "fallen apart", "shaken", "out of place", "nonworking", "impaired", "irreparable", "defective", "malfunctioning", "exhausted", 
  "wiped out", "fractured", "unbalanced", "distressed", "wrecked", "fragmentary", "punctured", "breached", "broken-up", "scattered", 
  "disabled", "shattered","powerful", "inspiring", "thoughtful", "uplifting", "motivational", "wise", "heartfelt","transformative", 
  "moving", "courageous", "resilient", "unbreakable", "hopeful", "empowering",
        "encouraging", "life-changing", "invincible", "remarkable", "strengthening", "enduring",
        "brave", "unwavering", "heroic", "fearless", "compassionate", "visionary", "groundbreaking",
        "exhilarating", "soothing", "healing", "compelling", "rejuvenating", "steadfast", "persistent",
        "undaunted", "incomparable", "invigorating", "graceful", "magnificent", "uplifting", "soul-stirring",
        "energizing", "faith-filled", "soulful", "enlightening", "impactful", "life-affirming", "encouraging",
        "joyful", "uplifting", "extraordinary", "radiant", "humbling", "motivating", "caring", "empathetic",
        "passionate", "optimistic", "grounded", "thrilling", "invincible", "outstanding", "joyous", "vibrant",
        "mindful", "steadfast", "determined", "unshakable", "tender", "balanced", "pioneering", "fearless",
        "refreshing", "heavenly", "supportive", "gracious", "dynamic", "heartened", "uplifted", "brilliant",
        "compassionate", "sensitive", "strong-willed", "driven", "nurturing", "fierce", "dedicated", "clear-headed",
        "luminous", "bold", "endless", "genuine", "carefree", "devoted", "steady", "timeless", "calm", "humble",
        "devout", "illuminating", "ecstatic", "passionate", "unfailing", "brave-hearted", "unbeaten", "majestic",
        "supportive", "daring", "empowering", "thriving", "selfless", "confident", "invincible", "inspiring",
        "positive", "unstoppable", "undaunted", "fiercely-loyal", "persevering", "optimistic", "fearless", "unfaltering",
        "unrelenting", "infallible", "reliable", "exceptional", "captivating", "meaningful", "hope-filled", "steadfast",
        "determined", "driven", "fearless", "ambitious", "trustworthy", "motivated", "persistent", "persistent",
        "intrepid", "courageous", "self-sufficient", "confident", "resolute", "undaunted", "inimitable", "brave",
        "indomitable", "undaunted", "honorable", "constant", "enthusiastic", "steady", "persistent", "brilliant",
        "unbreakable", "unshakable", "vibrant", "determined", "inspirational", "undaunted", "invulnerable", "persistent",
        "steadfast", "resilient", "unshaken", "loyal", "passionate", "unshakable", "valiant", "heartening", "motivated",
        "unbeatable", "focused", "enduring", "fearless", "valorous", "unfailing", "immovable", "persistent", "undaunted",
        "uncompromising", "resilient", "limitless", "untiring", "gritty", "resilient", "exceptional", "motivated",
        "heartening", "unshakeable", "magnificent", "unyielding", "hearty", "forceful", "inimitable", "outstanding",
        "defiant", "unchallenged", "unstoppable", "fearless", "undaunted", "unbeaten", "unflinching", "indestructible",
        "strong-willed", "unstoppable", "determined", "resilient", "unswerving", "indefatigable", "indomitable",
        "undaunted", "unwavering", "unassailable", "unrelenting", "infallible", "undaunted", "persistent", "undaunted",
        "relentless", "unyielding", "unbroken", "self-sustaining", "outstanding", "undaunted", "tenacious", "unbowed",
        "heroic", "indestructible", "indomitable", "unyielding", "bold", "unstoppable", "inexhaustible", "undaunted",
        "unfaltering", "unswerving", "heartening", "outstanding", "fearless", "resilient", "relentless", "unbreakable",
        "unrivaled", "unfailing", "tenacious", "unyielding", "brave", "strong-hearted", "unshakable", "undeterred",
        "incredible", "gritty", "unwavering", "boundless", "resilient", "strong-minded", "unbreakable", "invulnerable",
        "unassailable", "unstoppable", "untiring", "inspiring", "bold", "unstoppable", "unshaken", "undaunted",
        "steadfast", "unflinching", "untiring", "tenacious", "invincible", "unyielding", "remarkable", "unfaltering",
        "strong-willed", "self-assured", "reliable", "undaunted", "determined", "graceful", "focused", "determined",
        "unstoppable", "unconquerable", "powerful", "undaunted", "unbeatable", "brilliant", "unfailing", "tenacious",
        "persevering", "focused", "steady", "persistent", "faithful", "tireless", "invincible", "self-empowered", "valiant",
        "unstoppable", "magnificent", "unflinching", "unwavering", "indomitable", "bold", "unbreakable", "resilient",
        "courageous", "determined", "undaunted", "unyielding", "vibrant", "exceptional", "defiant", "gritty", "unshakable",
        "unyielding", "relentless", "indestructible", "invincible", "undaunted", "dynamic", "unrivaled", "untamed",
        "unstoppable", "fiercely-loyal", "unfaltering", "immovable", "strong-willed", "unbreakable", "unwavering",
        "relentless", "unyielding", "unyielding", "strong", "unbending", "steadfast", "unfaltering", "unbeaten", "unbeatable",
        "undaunted", "unconquerable", "heroic", "indestructible", "unstoppable", "undaunted", "undaunted", "inspirational"
    ]


    theme = [ "Motivational Quotes", "Inspiring Quotes", "Heartbreak Quotes", "Betrayal Quotes", "Karma Quotes", "Hope Quotes", "Wisdom Quotes", "Self-Love Quotes", "Overcoming Adversity Quotes", "Peace Quotes", "Empathy Quotes", "Healing Quotes", "Strength Quotes", "Gratitude Quotes", "Courage Quotes", "Success Quotes", "Leadership Quotes", "Confidence Quotes", "Faith Quotes", "Love Quotes", "Life Quotes", "Mindfulness Quotes", "Patience Quotes", "Friendship Quotes", "Forgiveness Quotes", "Dream Quotes", "Determination Quotes", "Positivity Quotes", "Growth Quotes", "Change Quotes", "Perspective Quotes", "Forgiving Yourself Quotes", "Compassion Quotes", "Ambition Quotes", "Self-Discipline Quotes", "Victory Quotes", "Peace of Mind Quotes", "Adventure Quotes", "Joy Quotes", "Self-Improvement Quotes", "Purpose Quotes", "Focus Quotes", "Inner Strength Quotes", "Balance Quotes", "Overcoming Fear Quotes", "Healing from Loss Quotes", "Transformation Quotes", "Mindset Quotes", "Resilience Quotes", "Trust Quotes", "Passion Quotes", "Persistence Quotes", "Gratitude for Life Quotes", "Acceptance Quotes", "Belief in Yourself Quotes", "Optimism Quotes", "Creativity Quotes", "Self-Respect Quotes", "Healing from Heartbreak Quotes", "Authenticity Quotes", "Happiness Quotes", "Change and Growth Quotes", "Spirituality Quotes", "Forgiving Others Quotes", "Kindness Quotes", "Self-Awareness Quotes", "Living in the Present Quotes", "Action Quotes", "Spiritual Growth Quotes", "Self-Worth Quotes", "Self-Care Quotes", "Mindset for Success Quotes", "Grief Quotes", "Renewal Quotes", "Learning from Mistakes Quotes", "Letting Go Quotes", "Strength in Adversity Quotes", "Self-Reflection Quotes", "Living with Purpose Quotes", "Healing from Betrayal Quotes", "Fearless Quotes", "Self-Empowerment Quotes", "Forgiveness and Healing Quotes", "Life Lessons Quotes", "Facing Challenges Quotes", "Empowering Quotes", "Authentic Living Quotes", "Persistence in the Face of Failure Quotes", "Hope for the Future Quotes", "Self-Motivation Quotes", "Overcoming Doubt Quotes", "Facing Uncertainty Quotes", "Achieving Peace Quotes", "Freedom Quotes", "Taking Responsibility Quotes", "Letting Go of the Past Quotes", "Moving Forward Quotes", "Healing Power of Love Quotes", "Self-Growth Quotes", "Finding Your Path Quotes", "Inner Peace Quotes", "Embracing Change Quotes", "Empowerment Through Struggles Quotes", "Living with Passion Quotes", "Victory Over Struggle Quotes", "Living Authentically Quotes", "Trust the Process Quotes", "Failure and Success Quotes", "Strength in Love Quotes", "Healing from Pain Quotes", "Learning from Failure Quotes", "Living in Gratitude Quotes", "Manifestation Quotes", "Self-Love and Acceptance Quotes", "Humility Quotes", "Awakening Quotes", "Self-Acceptance Quotes", "Forgiveness and Freedom Quotes", "Hope Through Struggles Quotes", "Finding Peace Within Quotes", "Power of Belief Quotes", "Positive Thinking Quotes", "Healing from Hurt Quotes", "Trusting the Journey Quotes", "Living Without Regrets Quotes", "Overcoming Setbacks Quotes", "Facing Your Fears Quotes", "Courage in the Face of Adversity Quotes", "Releasing Negativity Quotes", "Pushing Through Pain Quotes", "Finding Strength in Vulnerability Quotes", "Living with Intention Quotes", "Purposeful Living Quotes", "Strength Through Patience Quotes", "The Power of Forgiveness Quotes", "Rising Above Challenges Quotes", "Resilient Heart Quotes", "The Beauty of Life Quotes", "Taking the First Step Quotes", "Rising from the Ashes Quotes", "Empower Yourself Quotes", "Persistence Over Perfection Quotes", "Conquering Self-Doubt Quotes", "The Power of Letting Go Quotes", "Strength in Every Moment Quotes", "The Power of a Positive Mindset Quotes", "Rising Strong Quotes", "Find the Strength Within Quotes", "Breaking Free from Fear Quotes", "Transforming Pain into Power Quotes", "Chasing Your Dreams Quotes", "Rebuilding After Heartbreak Quotes", "Overcoming Loss Quotes", "Living for Yourself Quotes", "True Strength Quotes", "Lessons from Pain Quotes", "Power of Self-Belief Quotes", "Resilience in Tough Times Quotes", "Redemption Quotes", "Finding Peace Through Chaos Quotes", "Courage to Change Quotes", "Embrace Your Journey Quotes", "Unstoppable Spirit Quotes", "Rising Above the Storm Quotes", "Strength Comes from Struggle Quotes", "Faith in the Process Quotes", "The Art of Letting Go Quotes", "Courageous Living Quotes", "The Strength to Keep Going Quotes", "Courage to Face the Truth Quotes", "The Road to Healing Quotes", "Healing Starts from Within Quotes", "Inner Peace Through Self-Acceptance Quotes", "Strength in Forgiveness Quotes", "Healing from Regret Quotes", "Overcoming the Odds Quotes", "Bravery Through Pain Quotes", "Staying True to Yourself Quotes", "Rising from Pain Quotes", "Shifting Perspectives Quotes", "A Life Worth Living Quotes", "Moving On from Heartbreak Quotes", "Embracing New Beginnings Quotes", "Strength in Silence Quotes", "Trusting Yourself Quotes", "Healing Your Soul Quotes", "Transformation Through Trials Quotes", "Resilience in the Face of Failure Quotes", "Believing in Tomorrow Quotes", "Faith in Your Journey Quotes", "Living with Hope Quotes", "Embracing Your True Self Quotes", "Power of Self-Discovery Quotes", "Rebirth Quotes", "Life's Lessons Through Struggles Quotes", "Strength Beyond Limits Quotes", "The Gift of Resilience Quotes", "Overcoming the Darkness Quotes", "Trusting Your Path Quotes", "Finding Strength in Adversity Quotes", "Letting Go of Fear Quotes", "The Courage to Heal Quotes", "Building Resilience Through Pain Quotes", "Love Yourself First Quotes", "Through Struggle Comes Strength Quotes", "The Power of Persistence Quotes", "Learning to Trust Again Quotes", "Inner Peace Through Acceptance Quotes", "Resilience in Recovery Quotes", "Courage to Begin Again Quotes", "Healing with Time Quotes", "Strength is in the Struggle Quotes", "Belief in Your Own Power Quotes", "Perseverance Through Hardships Quotes", "Rise Above the Pain Quotes", "Faith in the Unseen Quotes", "The Strength to Keep Fighting Quotes" ]


    
    random_adjective = random.choice(adjectives)
    random_theme = random.choice(theme)
    
    prompt = f"""
    Generate an inspirational thought of the day in language {language}. The thought should be wise, motivating, and uplifting, and sound like something a thought leader or philosopher might say. It may be original or adapted from lesser-known works, but should not be famous or widely recognized. Attribute the thought to a real and notable author, philosopher, or thought leader, using their full name.

    The thought should be inspired by the theme: {random_theme}, and should feel {random_adjective}, impactful, and inspiring. Make the message broad and relatable for a wide audience, not narrowly focused.
    
    Also include:
    
    A concise, memorable title capturing the essence of the thought.
    
    A short, insightful description explaining its meaning and relevance.
    
    A list of 10–25 diverse, relevant, single-word, lowercase tags related to the thought.


    Use the following JSON schema:
    {{
        "quote": "A new and unique inspiring, wise,heart break, betrayal, revenge, karma, comeback, heart-touching thought for the day from a diffent authors. (string)",
        "title": "A short title that captures the essence of the thought for the day with 90 charcaters or 90 tokens which ever less. (string)",
        "description": "A brief description explaining the meaning of the thought for the day. (string)",
        "tags": ["A list of 10-25 relevant tags. (array of strings)"]
    }}
    
    
    Example:
    {{
        "quote": "The only way to do great work is to love what you do. - Steve Jobs",
        "title": "Passion for Work",
        "description": "This thought for the day emphasizes the importance of finding passion in your work. It suggests that genuine fulfillment and excellence come from pursuing what you truly love.",
        "tags": ["passion", "work", "motivation", "inspiration", "success"]
    }}
    
    Return only the JSON object. Do not include any extra text. Generate a new and unique thought for the day each time.
    """
    
    try:
        response = model.generate_content(prompt, generation_config=types.GenerationConfig(
            max_output_tokens=800,
            temperature=0.9,
            top_p=0.95,
            top_k=500,
            candidate_count=1, 
        ))
        if not response.text:
            print("Error: Gemini model returned an empty response.")
            sendMail(None,"Error: Gemini model returned an empty response : generateQuoteEnglish : 72")
            raise ValueError("Empty response from Gemini model.")
    
        raw_text = response.text
        data = json.loads(raw_text.strip('```json\n').strip('```'))
    
        # Validate the JSON data
        if isinstance(data, dict) and "quote" in data and "title" in data and "description" in data and "tags" in data and isinstance(data["tags"], list):
            quote = data["quote"]
            title = data["title"]
            description = data["description"]
            tags = data["tags"]
            # Join tags into a single string with a separator (e.g., comma)
            joined_tags = ",".join(data["tags"])
            
            # Ensure the length of the joined tags is no more than 500 characters
            if len(joined_tags) > 500:
                # If it's too long, truncate it to 500 characters, ensuring the last tag is not cut off mid-way
                joined_tags = joined_tags[:489]
            
            # Assign the modified string back to the tags field (if necessary)
            data["tags"] = joined_tags.split(",")  # Optional: split back into list if needed
            tags =data["tags"]
    
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
                data["title"] = new_title[:99] 
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("Quote data saved to quote_data.json")
            return data
        else:
            print("Invalid JSON structure.")
            print("Response Text:", response.text)
            sendMail(None,"Invalid JSON structure : generateQuoteEnglish : 111")
    
    except json.JSONDecodeError as e:
        print(f"Error: Could not parse JSON response. Error: {e} : generateQuoteEnglish : 114")
        sendMail(None,"Could not parse JSON response")
    except AttributeError:
        print("Error: Could not extract quote from response. Check the model output.")
        sendMail(None,'Error: Could not extract quote from response. Check the model output. : generateQuoteEnglish : 118')
    except ValueError as ve:
        print(f"ValueError: {ve}")
        sendMail(None,f"{'ValueError'} : generateQuoteEnglish : 121")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sendMail(None,"An unexpected error occurred : generateQuoteEnglish : 123")