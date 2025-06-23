import os
from dotenv import load_dotenv
from google import genai
import logging
from project_logger import setup_logger

load_dotenv()
api_key = os.getenv("API_KEY")
model="gemini-2.5-flash"
logger = setup_logger(os.getenv("log_level"))


def call_genai(prompt: str) -> str:
    """
    Calls the Google GenAI API to generate content.
    """
    
    if not api_key:
        logger.error("API_KEY not found in environment variables. Please check your .env file.")
        return "API_KEY is missing. Cannot proceed."
    if not prompt:
        logger.error("Prompt is empty. Please provide a valid prompt.")
        return "Prompt is empty. Cannot proceed."
    if not model:
        logger.error("Model is not specified. Please set a valid model.")
        return "Model is not specified. Cannot proceed."
    
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        logger.error(f"Error calling GenAI: {e}")
        return None


if __name__ == "__main__":
    response = call_genai("Explain how AI works in a few words")
    if response:
        print(response)