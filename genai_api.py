import os
import logging
from dotenv import load_dotenv
from google import genai
from project_logger import setup_logger

load_dotenv()
logger = setup_logger(os.getenv("log_level"))

def call_genai(prompt: str) -> str:
    """
    Calls the Google GenAI API to generate content.
    Loads API_KEY and model from environment variables.

    Args:
        prompt (str): The text prompt to send to the GenAI model.

    Returns:
        str: The generated text content from the model, or None if an error occurs.
    """
    api_key = os.getenv("API_KEY")
    model = os.getenv("MODEL")
    
    if not api_key:
        logger.error("API_KEY not found in environment variables. Please check your .env file.")
        return None
    if not prompt:
        logger.error("Prompt is empty. Please provide a valid prompt.")
        return None
    if not model:
        logger.error("Model is not specified. Please set a valid model (e.g., in .env as GEMINI_MODEL).")
        return None
    
    try:
        logger.info(f"Attempting to call GenAI")
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        logger.info("Successfully received response from GenAI API.")
        return response.text
    except Exception as e:
        logger.error(f"Error calling GenAI API: {e}", exc_info=True)
        return None