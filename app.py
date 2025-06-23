import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")

from google import genai

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain how AI works in a few words",
)

print(response.text)