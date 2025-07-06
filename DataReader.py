import json
import csv
from project_logger import setup_project_logger
from config import(
    QUERY_TYPES_FILE, PROMPT1_FILE, PROMPT2_FILE, PROMPT3_FILE,
    COLLECTION_INFO_DIR
)

class DataReader:
    logger = setup_project_logger("DataReader")
    
    def __init__(self):
        self.query_types_file = QUERY_TYPES_FILE
        self.prompt1_file = PROMPT1_FILE
        self.prompt2_file = PROMPT2_FILE
        self.prompt3_file = PROMPT3_FILE
        self.collection_info_dir = COLLECTION_INFO_DIR

    def _read_json_file(self, filename):
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            self.logger.error(f"File {filename} not found.")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON in file {filename}: {str(e)}")
            raise
        
    def _read_file(self, filename):
        try:
            with open(filename, 'r') as file:
                data = file.read()
                return data
        except FileNotFoundError:
            self.logger.error(f"File {filename} not found.")
            raise
        except Exception as e:
            self.logger.error(f"Failed to read secrets file {filename}: {str(e)}")
            raise

    def read_query_types_file(self):
        return self._read_json_file(QUERY_TYPES_FILE)

    def read_collection_info_file(self, collection_file_name):
        collection_info_path = f"{self.collection_info_dir}/{collection_file_name}"
        return self._read_json_file(collection_info_path)

    def read_prompts_files(self):
        prompt1 = self._read_file(PROMPT1_FILE)
        prompt2 = self._read_file(PROMPT2_FILE)
        prompt3 = self._read_file(PROMPT3_FILE)
        return prompt1, prompt2, prompt3
