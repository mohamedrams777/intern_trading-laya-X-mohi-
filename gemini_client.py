import requests
import os
from config import Config
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def ask_gemini(prompt):
    """
    Call Gemini API to generate text based on the prompt.
    Uses the API key from Config (which reads from .env)
    """
    GEMINI_API_KEY = Config.GEMINI_API_KEY
    
    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY not configured in .env file"
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"Gemini API Error {response.status_code}: {response.text}"
    except requests.exceptions.Timeout:
        return "Error: Gemini API request timed out"
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to reach Gemini API: {str(e)}"
    except (KeyError, IndexError) as e:
        return f"Error: Unexpected response format from Gemini API: {str(e)}"
