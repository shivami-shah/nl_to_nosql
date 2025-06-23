import os
from dotenv import load_dotenv
import logging
from project_logger import setup_logger
from genai_api import call_genai
from queries_type_processor import get_query_types

load_dotenv()

prompt1_file = os.getenv("PROMPT1_FILE")
if not prompt1_file:
    logging.error("PROMPT1_FILE not found in environment variables.")
    exit(1)

prompt2_file = os.getenv("PROMPT2_FILE")
if not prompt2_file:
    logging.error("PROMPT2_FILE not found in environment variables.")
    exit(1)

prompt3_file = os.getenv("PROMPT3_FILE")
if not prompt3_file:
    logging.error("PROMPT3_FILE not found in environment variables.")
    exit(1)
    
query_types = get_query_types()
if not query_types:
    logging.error("No query types found.")
    exit(1)
    
    
for i in range(0, 1): # TODO: Change to len(query_types) when ready
    
    query_type = query_types[i]

    generated_queries = call_genai(prompt1_file, prompt_addon=query_type, is_file=True)
    if not generated_queries:
        logging.error("Failed to get a response from GenAI. No queries generated.")
        exit(1)
        
    prompt_addon = query_type + "\n\n\nQueries:\n" + generated_queries    
    generated_questions = call_genai(prompt2_file, prompt_addon=prompt_addon, is_file=True)    
    if not generated_questions:
        logging.error("Failed to get a response from GenAI. No questions generated.")
        exit(1)

    generated_answers = call_genai(prompt3_file, prompt_addon=prompt_addon, is_file=True)
    if not generated_answers:
        logging.error("Failed to get a response from GenAI. No answers generated.")
        exit(1)
        
    print(generated_answers)
    