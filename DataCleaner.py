from config import PROMPT_RESULT_DIR        
from project_logger import setup_project_logger

class DataCleaner:
    logger = setup_project_logger("DataCleaner")
    
    def __init__(self):
        self.output_dir = PROMPT_RESULT_DIR

    def write_to_text(self, collection_name: str, query_type:str, output: str):
        query_type = ''.join(filter(str.isalpha, query_type))
        file_name = PROMPT_RESULT_DIR / f"{collection_name}_{query_type}.txt"
        with open(file_name, "w") as file:
            file.write(output)
        self.logger.info(f"Data written to {file_name}")
        
            
