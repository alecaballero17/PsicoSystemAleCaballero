import requests
import json
import decouple

api_key = decouple.config("GROQ_API_KEY", default=None)
print("API_KEY:", api_key[:10] if api_key else "None")

data = {
    "model": "llama3-8b-8192",
    "messages": [
        {"role": "system", "content": "hola"},
        {"role": "user", "content": "hola"}
    ],
    "temperature": 0.7,
    "max_tokens": 256,
    "top_p": 1,
    "stream": False
}

response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {api_key}"}, json=data)
print(response.status_code)
print(response.json())
