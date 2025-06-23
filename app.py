import os
from dotenv import load_dotenv
import logging
from project_logger import setup_logger
from genai_api import call_genai
from queries_type_processor import get_query_types
from write_output import write_to_files

load_dotenv()
logger = setup_logger(os.getenv("LOG_LEVEL"))
file_prefix = "ForecastAccuracy"

prompt1_file = os.getenv("PROMPT1_FILE")
if not prompt1_file:
    logger.error("PROMPT1_FILE not found in environment variables.")
    exit(1)

prompt2_file = os.getenv("PROMPT2_FILE")
if not prompt2_file:
    logger.error("PROMPT2_FILE not found in environment variables.")
    exit(1)

prompt3_file = os.getenv("PROMPT3_FILE")
if not prompt3_file:
    logger.error("PROMPT3_FILE not found in environment variables.")
    exit(1)
    
query_types = get_query_types()
if not query_types:
    logger.error("No query types found.")
    exit(1)


for query_type in query_types:

    generated_queries = call_genai(prompt1_file, prompt_addon=query_type, is_file=True)
    if not generated_queries:
        logger.error("Failed to get a response from GenAI. No queries generated.")
        exit(1)
        
    prompt_addon = query_type + "\n\n\nQueries:\n" + generated_queries    
    generated_questions = call_genai(prompt2_file, prompt_addon=prompt_addon, is_file=True)    
    if not generated_questions:
        logger.error("Failed to get a response from GenAI. No questions generated.")
        exit(1)

    generated_answers = call_genai(prompt3_file, prompt_addon=prompt_addon, is_file=True)
    if not generated_answers:
        logger.error("Failed to get a response from GenAI. No answers generated.")
        exit(1)

    file_suffix = query_type.replace(" ", "_").replace(".", "") + "_output.txt"

    status = write_to_files(generated_queries, generated_questions, generated_answers, file_prefix, file_suffix)
    if not status:
        logger.error("Failed to write output files.")
        exit(1)
    else:
        logger.info(f"Output files written successfully for query type: {query_type}")