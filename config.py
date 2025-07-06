#------------------------------- LOGGING -------------------------------
import logging
LOGGING_LEVEL = logging.DEBUG

#----------------------------- DIRECTORIES -----------------------------
from pathlib import Path
import os
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = DATA_DIR / "logs"
OUTPUT_DIR = DATA_DIR / "output"
QUERIES_DIR = DATA_DIR / "queries"
COLLECTION_INFO_DIR = DATA_DIR / "collection_info"

# Ensure the directories exist
LOGS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
QUERIES_DIR.mkdir(exist_ok=True)
COLLECTION_INFO_DIR.mkdir(exist_ok=True)

#------------------------ TRAINING DATA GENERATION ----------------------
from dotenv import load_dotenv
load_dotenv()

API_KEY = (os.getenv("API_KEY"))
EXTERNAL_MODEL="gemini-2.5-flash"

QUERY_TYPES_FILE = QUERIES_DIR / "query_types.json"
PROMPT1_FILE = QUERIES_DIR / "sql_query_generation.secrets"
PROMPT2_FILE = QUERIES_DIR / "question_generation.secrets"
PROMPT3_FILE = QUERIES_DIR / "answer_generation.secrets"