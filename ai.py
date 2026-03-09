import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

URL = "https://openrouter.ai/api/v1/chat/completions"


def ask_ai(prompt):

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/llama-3-8b-instruct",
        "max_tokens": 40,
        "messages": [
            {
                "role": "system",
                "content": "You are a voice assistant. Reply briefly."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:

        r = requests.post(URL, headers=headers, json=data, timeout=20)
        result = r.json()

        print("AI response:", result)

        if "choices" not in result:
            return "AI error."

        return result["choices"][0]["message"]["content"]

    except Exception as e:
        print("AI request failed:", e)
        return "AI request failed."