import os
import logging
from dotenv import load_dotenv
from google import genai
from project_logger import setup_logger

load_dotenv()
logger = setup_logger(os.getenv("LOG_LEVEL"))

def _read_prompt_from_file(file_path: str) -> str | None:
    """
    Reads the content of a prompt from a specified file path.
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"Prompt file not found: {file_path}")
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            prompt_content = f.read()
        logger.info(f"Prompt loaded successfully from {file_path}")
        return prompt_content
    except IOError as e:
        logger.error(f"Error reading prompt file {file_path}: {e}", exc_info=True)
        return None
    

def call_genai(prompt_source: str, prompt_addon: str = None, is_file: bool = False) -> str | None:
    """
    Calls the Google GenAI API to generate content.
    Loads API_KEY and model from environment variables.

    Args:
        prompt_source (str): The text prompt itself, or the path to a file containing the prompt.
        is_file (bool): If True, prompt_source is treated as a file path to read the prompt from.

    Returns:
        str: The generated text content from the model, or None if an error occurs.
    """
    api_key = os.getenv("API_KEY")
    model = os.getenv("MODEL")
    
    if not api_key:
        logger.error("API_KEY not found in environment variables. Please check your .env file.")
        return None
    if not model:
        logger.error("Model is not specified. Please set a valid model (e.g., in .env as GEMINI_MODEL).")
        return None
    
    if is_file:
        prompt_content = _read_prompt_from_file(prompt_source)
        if prompt_content is None:
            logger.error(f"Failed to read prompt from file: {prompt_source}. Aborting GenAI call.")
            return None
    else:
        prompt_content = prompt_source
        
    if not prompt_content:
        logger.error("Prompt is empty. Please provide a valid prompt.")
        return None
    
    if prompt_addon:
        prompt_content += f"\n{prompt_addon}"
        logger.info(f"Addon to prompt applied.")
    
    try:
        logger.info(f"Attempting to call GenAI")
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=prompt_content,
        )
        logger.info("Successfully received response from GenAI API.")
        return response.text
    except Exception as e:
        logger.error(f"Error calling GenAI API: {e}", exc_info=True)
        return None
    
    
if __name__ == "__main__":
    response = call_genai("Explain how AI works in a few words")
    if response:
        print(response)