import os
from dotenv import load_dotenv
import logging
from project_logger import setup_logger
from genai_api import call_genai

load_dotenv()

prompt1_file = os.getenv("PROMPT1_FILE")
if not prompt1_file:
    logging.error("PROMPT1_FILE not found in environment variables.")
    exit(1)

response = call_genai(prompt1_file, is_file=True)
if response:
    print(response)