import csv
import os
from config import PROMPT_RESULT_DIR, OUTPUT_DIR, ERROR_FILES_DIR, DB_ERRORS_DIR
from project_logger import setup_project_logger
from DataReader import DataReader
from DBManager import DBManager

class DataCleaner:
    logger = setup_project_logger("DataCleaner")
    
    def __init__(self):
        self.output_dir = PROMPT_RESULT_DIR
        self.reader = DataReader()
        self.db_manager = DBManager()
        
    def _write_to_file(self, content:str, filename: str):
        try:
            with open(filename, 'w') as file:
                file.write(content)
            self.logger.info(f"Data written to {filename}")
        except Exception as e:
            self.logger.error(f"Failed to write data to {filename}: {str(e)}")
            
    def _append_to_file(self, content:str, filename: str):
        try:
            with open(filename, 'a') as file:
                file.write(content)
            self.logger.info(f"Data appended to {filename}")
        except Exception as e:
            self.logger.error(f"Failed to write data to {filename}: {str(e)}")
            
    def _write_to_csv(self, filename: str, *args):
        lists_to_zip = []
        for arg in args:
            if isinstance(arg, list):
                lists_to_zip.append(arg)
            else:
                self.logger.warning(f"Warning: Argument '{arg}' is not a list and will be skipped.")

        if not lists_to_zip:
            self.logger.warning("No lists found write to file.")
            return
        
        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Question", "Answer", "Query"])  # header row
                for row in zip(*lists_to_zip):
                    writer.writerow(row)
            self.logger.info(f"Data written to {filename}")                
        except Exception as e:
            self.logger.error(f"Failed to write data to {filename}: {str(e)}")

    def write_prompt_output(self, collection_name: str, query_type:str, output: str):
        query_type = ''.join(filter(str.isalpha, query_type))
        file_name = PROMPT_RESULT_DIR / f"{collection_name}_{query_type}.txt"
        self._write_to_file(output, file_name)
    
    def _seperate_sections(self):
        queries_end_index = self.content.index("QUESTIONS")
        questions_end_index = self.content.index("ANSWERS")            
        self.queries = self.content[:queries_end_index].split('\n')
        self.questions = self.content[queries_end_index:questions_end_index].split('\n')[1:]
        self.answers = self.content[questions_end_index:].split('\n')[1:]
        
    def _validate_queries(self, file:str, mappings:dict):
        invalid_queries = []
        for i, query in enumerate(self.queries):
            if query.startswith("db."):
                
                # Replace actual field names from mappings
                mapped_query = str(query)
                for key, value in mappings.items():
                    mapped_query = mapped_query.replace(f'{key}', f'{value}')

                validated_query = self.db_manager.validate_query(mapped_query)
                if not validated_query:
                    invalid_queries.append(mapped_query)
                    self.queries[i] = ""
            else:
                self.queries[i] = ""
        self.queries = list(filter(None, self.queries))   
        
        # Convert the list "invalid_queries" to string, with each element in a new line
        if len(invalid_queries) > 0:
            invalid_queries_str = f"\nINVALID QUERIES-{file}\n" + '\n'.join(invalid_queries) + '\n'
            self._append_to_file(invalid_queries_str, self.db_error_file_name)

    def _extract_to_lists(self):
                
        newlines_questions = []
        newlines_answers = []
        for i, text in enumerate(self.questions):
            if len(text) == 0:
                newlines_questions.append(i)                    
        for i, text in enumerate(self.answers):
            if len(text) == 0:
                newlines_answers.append(i)
        
        self.all_questions_list = []
        self.all_answers_list = []
        self.all_queries_list = []
        missing_questions_answers = []
        
        for query in self.queries:
            try:
                questions_index = next(i for i, q in enumerate(self.questions) if query.lower() in q.lower())
                answers_index = next(i for i, q in enumerate(self.answers) if query.lower() in q.lower())
            except StopIteration:
                self.logger.warning(f"No question found with query: {query}")
                missing_questions_answers.append(query)
                continue
                       
            questions_list = []
            answers_list = []
            
            temp_indexes = [i for i in newlines_questions if i > questions_index]
            next_question_index = min(temp_indexes) if temp_indexes else len(self.questions)-1
            temp_indexes = [i for i in newlines_answers if i > answers_index]
            next_answer_index = min(temp_indexes) if temp_indexes else len(self.answers)-1
            
            if next_question_index + 1 == len(self.questions):
                next_question_index += 1
            if next_answer_index + 1 == len(self.answers):
                next_answer_index += 1            
            
            questions_list = self.questions[questions_index:next_question_index]
            answers_list = self.answers[answers_index:next_answer_index]
            
            questions_list = [q for q in questions_list if "Question" in q]
            questions_list = [q.replace("*", "").strip() for q in questions_list]
            questions_list = [q.split(":")[1].strip() for q in questions_list]

            questions_list_append = ([c.split(":")[1].strip() for c in answers_list if "Question" in c])
            questions_list += questions_list_append
            
            answers_list = [c.split(":")[1].strip() for c in answers_list if "Answer" in c]
            
            extra_questions = len(questions_list) - len(answers_list)
            answers_list_extra = [answers_list[0]] * extra_questions
            answers_list += answers_list_extra
            
            query_list = [query]*len(questions_list)
            
            self.all_questions_list += questions_list
            self.all_answers_list += answers_list
            self.all_queries_list += query_list
        
        if len(missing_questions_answers)>0:
            missing_questions_answers_str = "\nMISSING QUESTIONS OR ANSWERS:" + '\n' + '\n'.join(missing_questions_answers) + "\n"
            self._append_to_file(missing_questions_answers_str, self.db_error_file_name)

    def clean_prompt_output(self):

        for file in os.listdir(PROMPT_RESULT_DIR):
            self.collection_name = file.split("_")[0]
            mappings = self.reader.read_collection_info_file(f"{self.collection_name}.json")["mappings"]
            self.db_error_file_name = DB_ERRORS_DIR / f"{self.collection_name}_invalid_queries.txt"
            try:
                self.logger.info(f"Prompt output started processed for {file}")
                self.content = self.reader.read_prompt_output_file(file)
                
                self._seperate_sections()
                self._validate_queries(file, mappings)
                self._extract_to_lists()
                output_file = file.replace(".txt", ".csv")
                
                mapped_query_list = []
                for query in self.all_queries_list:
                    # Replace actual field names from mappings
                    for key, value in mappings.items():
                        query = str(query).replace(key, value)
                    mapped_query_list.append(query)
                
                self._write_to_csv(OUTPUT_DIR / output_file, self.all_questions_list, self.all_answers_list, mapped_query_list)
                self._write_to_file
               
            except Exception as e:
                src = PROMPT_RESULT_DIR / file
                dest = ERROR_FILES_DIR / file
                import shutil
                shutil.copy(src, dest)
                self.logger.error(f"An unexpected error occurred during processing {file}: {e}")


if __name__ == "__main__":
    # Delete all files in error directories
    for filename in ERROR_FILES_DIR.iterdir():
        if filename.is_file():
            os.remove(filename)
    for filename in DB_ERRORS_DIR.iterdir():
        if filename.is_file():
            os.remove(filename)
            
    cleaner = DataCleaner()
    cleaner.clean_prompt_output()
