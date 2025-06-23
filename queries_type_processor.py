import json
import os
import logging
from dotenv import load_dotenv
from google import genai
from project_logger import setup_logger

load_dotenv()
logger = setup_logger(os.getenv("LOG_LEVEL"))

def _load_sections_from_json(file_path):
    """
    Loads section data from a JSON file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        list: A list of dictionaries containing the section data, or None if an error occurs.
    """
    if not os.path.exists(file_path):
        logger.error(f"JSON file not found at {file_path}")
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Successfully loaded JSON data from {file_path}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {file_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred while reading {file_path}: {e}")
        return None
    
def get_query_types():
    """
    Processes the sections data and prints each section with its subsections.

    Args:
        sections_data (list): A list of dictionaries containing section data.
    """
    file_path = os.getenv("QUERY_TYPES_FILE")
    if not file_path:
        logger.error("QUERY_TYPES_FILE not found in environment variables.")
        return
    
    sections_data = _load_sections_from_json(file_path)
    if not sections_data:
        return
    
    query_types_list = []
    for section_data in sections_data:
        section_title = section_data["section"]
        for subsection_title in section_data["subsections"]:
            query_types_list.append(f"{section_title} {subsection_title}")

    return query_types_list

if __name__ == "__main__":
    query_types = get_query_types()
    print(query_types)
