import json
import csv
from project_logger import setup_project_logger
from config import(
    QUERY_TYPES_FILE, PROMPT1_FILE, PROMPT2_FILE, PROMPT3_FILE, PROMPT4_FILE,
    COLLECTION_INFO_DIR, PROMPT_RESULT_DIR
)

class DataReader:
    logger = setup_project_logger("DataReader")
    
    def __init__(self):
        self.query_types_file = QUERY_TYPES_FILE
        self.prompt1_file = PROMPT1_FILE
        self.prompt2_file = PROMPT2_FILE
        self.prompt3_file = PROMPT3_FILE
        self.prompt4_file = PROMPT4_FILE
        self.collection_info_dir = COLLECTION_INFO_DIR

    def _read_json_file(self, filename):
        """Reads a JSON file and returns its content.

        Args:
            filename (str): The path to the JSON file.

        Returns:
            data (dict): The content of the JSON file.

        """
        if str(filename).split('.')[-1] != "json":
            self.logger.error(f"File {filename} is not a JSON file.")
            return False
        
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

    def read_query_types_file(self, file=QUERY_TYPES_FILE):
        return self._read_json_file(file)

    def read_collection_info_file(self, collection_file_name):
        collection_info_path = f"{self.collection_info_dir}/{collection_file_name}"
        return self._read_json_file(collection_info_path)

    def read_prompts_files(self):
        prompt1 = self._read_file(PROMPT1_FILE)
        prompt2 = self._read_file(PROMPT2_FILE)
        prompt3 = self._read_file(PROMPT3_FILE)
        prompt4 = self._read_file(PROMPT4_FILE)
        return prompt1, prompt2, prompt3, prompt4
    
    def read_prompt_output_file(self, filename):
        return self._read_file(PROMPT_RESULT_DIR / filename)
