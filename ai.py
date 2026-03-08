import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

def ask_ai(prompt):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/llama-3-8b-instruct",
        "max_tokens": 30,
        "messages": [
            {
                "role": "system",
                "content": "You are a voice assistant. Reply in very short sentences (max 12 words). Clear and simple."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    result = response.json()

    print("API RESPONSE:", result)

    if "choices" not in result:
        return "AI Error: " + str(result)

    return result["choices"][0]["message"]["content"]