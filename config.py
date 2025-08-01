#------------------------------- LOGGING -------------------------------
import logging
LOGGING_LEVEL = logging.DEBUG

#----------------------------- DIRECTORIES -----------------------------
from pathlib import Path
import os
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data" / "system"
USER_DIR = PROJECT_ROOT / "data" / "user"
LOGS_DIR = DATA_DIR / "logs"
PROMPT_RESULT_DIR = DATA_DIR / "prompt_results"
OUTPUT_DIR = DATA_DIR / "output"
QUERIES_DIR = DATA_DIR / "queries"
COLLECTION_INFO_DIR = DATA_DIR / "collection_info"
OUTPUT_CSV_DIR = OUTPUT_DIR / "output_csv"
ERROR_FILES_DIR = OUTPUT_DIR / "error_files"
DB_ERRORS_DIR = OUTPUT_DIR / "db_errors"

#------------------------ TRAINING DATA GENERATION ----------------------
from dotenv import load_dotenv
load_dotenv()

API_KEY = (os.getenv("API_KEY"))
EXTERNAL_MODEL="gemini-2.5-flash"

QUERIES_DIR.mkdir(exist_ok=True)
QUERY_TYPES_FILE = QUERIES_DIR / "query_types.json"
PERMENANT_QUERY_TYPES_FILE = QUERIES_DIR / "query_types_perm.json"
PROMPT1_FILE = QUERIES_DIR / "sql_query_generation.secrets"
PROMPT2_FILE = QUERIES_DIR / "question_generation.secrets"
PROMPT3_FILE = QUERIES_DIR / "search_terms_generation.secrets"
PROMPT4_FILE = QUERIES_DIR / "answer_generation.secrets"


#----------------------------- DB CONNECTION ----------------------------
DATABASE="NL2SQL"
HOST="localhost"
PORT=27017


#-------------------------------- OTHERS --------------------------------
MAX_WORKERS = 3