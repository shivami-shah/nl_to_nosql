from config import OUTPUT_DIR        
from project_logger import setup_project_logger

class DataCleaner:
    logger = setup_project_logger("DataCleaner")
    
    def __init__(self):
        self.output_dir = OUTPUT_DIR

    def write_to_text(self, collection_name: str, query_type:str, output: str):
        query_type = ''.join(filter(str.isalpha, query_type))
        file_name = OUTPUT_DIR / f"{collection_name}_{query_type}.txt"
        with open(file_name, "w") as file:
            file.write(output)
        self.logger.info(f"Data written to {file_name}")
        
            
