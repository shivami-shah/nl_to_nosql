import csv
import re
import os
from config import (
    PROMPT_RESULT_DIR, OUTPUT_DIR,
    ERROR_FILES_DIR, DB_ERRORS_DIR,
    OUTPUT_CSV_DIR, COLLECTION_INFO_DIR)
from project_logger import setup_project_logger
from DataReader import DataReader
from DBManager import DBManager

class DataCleaner:
    logger = setup_project_logger("DataCleaner")
    
    def __init__(self):
        PROMPT_RESULT_DIR.mkdir(exist_ok=True)
        OUTPUT_DIR.mkdir(exist_ok=True)        
        OUTPUT_CSV_DIR.mkdir(exist_ok=True)
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

    def write_prompt_output(self, collection_name: str, query_type: dict, output: str):
        query_type_str = str(query_type["section"]) + str(query_type["subsection"])
        numbers = re.findall(r'\d+', query_type_str.replace(".", ""))
        query_type = '_'.join(numbers)
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
            self.logger.info(f"Processing query number {i+1} of {len(self.queries)}")
            if query.startswith("db."):
                
                # Replace actual field names from mappings
                mapped_query = str(query)
                for key, value in mappings.items():
                    mapped_query = mapped_query.replace(f'{key}', f'{value}')

                validated_query = self.db_manager.validate_query(mapped_query)
                if not validated_query:
                    self.logger.info(f"Invalid query: {mapped_query}")
                    invalid_queries.append(mapped_query)
                    self.queries[i] = ""
            else:
                self.queries[i] = ""
        self.queries = list(filter(None, self.queries))   
        
        # Convert the list "invalid_queries" to string, with each element in a new line
        if len(invalid_queries) > 0:
            invalid_queries_str = f"\nINVALID QUERIES-{file}\n" + '\n'.join(invalid_queries) + '\n'
            self._append_to_file(invalid_queries_str, self.db_error_file_name)

    def _extract_to_lists(self, file):
                
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
            
            cleaned_answers_list = []
            for line in answers_list:
                if "Answer" in line:
                    parts = line.split(':')
                    cleaned_answers_list.append(':'.join(parts[1:]).strip())
            answers_list = cleaned_answers_list
            
            extra_questions = len(questions_list) - len(answers_list)
            answers_list_extra = [answers_list[0]] * extra_questions
            answers_list += answers_list_extra
            
            query_list = [query]*len(questions_list)
            
            self.all_questions_list += questions_list
            self.all_answers_list += answers_list
            self.all_queries_list += query_list
        
        if len(missing_questions_answers)>0:
            missing_questions_answers_str = f"\nMISSING QUESTIONS OR ANSWERS-{file}:" + '\n' + '\n'.join(missing_questions_answers) + "\n"
            self._append_to_file(missing_questions_answers_str, self.db_error_file_name)
    
    def clean_file_names(self):
        prompt_result_files = []
        for filename in os.listdir(PROMPT_RESULT_DIR):
            parts = filename.split('_')
            parts = parts[:4]
            if '.' in parts[-1]:
                parts[-1] = parts[-1].split('.')[0]
            new_filename = "_".join(parts) + ".txt"
            old_path = os.path.join(PROMPT_RESULT_DIR, filename)
            new_path = os.path.join(PROMPT_RESULT_DIR, new_filename)
            if not os.path.exists(new_path):
                os.rename(old_path, new_path)
                self.logger.info(f"Renamed file {old_path} to {new_path}")                
            prompt_result_files.append(new_filename)
        self.logger.info("File names cleaned successfully.")
        return prompt_result_files
        
    def filter_files(self, files):
        query_types = self.reader.read_query_types_file()
        
        files_prefixes = []
        for file in os.listdir(COLLECTION_INFO_DIR):
            files_prefixes.append(file.replace(".json", ""))
        
        files_suffixes = []
        for section_info in query_types:
            section = section_info["section"]
            for subsection in section_info["subsections"]:
                suffix = "_" + "".join(re.findall(r'\d', section)) \
                    + "_" + "".join(re.findall(r'\d', subsection)) \
                    + ".txt"
                files_suffixes.append(suffix)
        
        prefix_filtered_files = []
        for file in files:
            for file_prefix in files_prefixes:
                if file.startswith(file_prefix):
                    prefix_filtered_files.append(file)
                    break        
        
        files_to_process = []
        for file in prefix_filtered_files:
            for file_suffix in files_suffixes:
                if file.endswith(file_suffix):
                    files_to_process.append(file)
                    break
                
        return files_to_process
        
    def clean_prompt_output(self):        
        files = self.clean_file_names()
        files_to_process = self.filter_files(files)
        
        for file in files_to_process:
            parts = file.split("_")
            self.collection_name = "_".join(parts[:-2])
            mappings = self.reader.read_collection_info_file(f"{self.collection_name}.json")["mappings"]
            self.db_error_file_name = DB_ERRORS_DIR / f"{self.collection_name}_invalid_queries.txt"
            try:
                self.logger.info(f"Prompt output started processed for {file}")
                self.content = self.reader.read_prompt_output_file(file)
                
                self._seperate_sections()
                self._validate_queries(file, mappings)
                
                output_file = file.replace(".txt", ".csv")
                if len(self.queries) > 0:
                    self._extract_to_lists(file)
                    
                    mapped_query_list = []
                    for query in self.all_queries_list:
                        # Replace actual field names from mappings
                        for key, value in mappings.items():
                            query = str(query).replace(key, value)
                        mapped_query_list.append(query)
                        
                    self._write_to_csv(OUTPUT_CSV_DIR / output_file, self.all_questions_list, self.all_answers_list, mapped_query_list)
                else:
                    self.logger.info(f"No queries found for {file}")
                    self.all_questions_list = []
                    self.all_answers_list = []
                    self._write_to_csv(ERROR_FILES_DIR / output_file, self.all_questions_list, self.all_answers_list, self.queries)

            except Exception as e:
                src = PROMPT_RESULT_DIR / file
                dest = ERROR_FILES_DIR / file
                import shutil
                shutil.copy(src, dest)
                self.logger.error(f"An unexpected error occurred during processing {file}: {e}")


if __name__ == "__main__":
    # # Delete all files in error directories
    # for filename in ERROR_FILES_DIR.iterdir():
    #     if filename.is_file():
    #         os.remove(filename)
    # for filename in DB_ERRORS_DIR.iterdir():
    #     if filename.is_file():
    #         os.remove(filename)
            
    cleaner = DataCleaner()
    cleaner.clean_prompt_output()
