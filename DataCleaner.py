import csv
import os
from config import PROMPT_RESULT_DIR, OUTPUT_DIR, ERROR_FILES_DIR
from project_logger import setup_project_logger
from DataReader import DataReader

class DataCleaner:
    logger = setup_project_logger("DataCleaner")
    
    def __init__(self):
        self.output_dir = PROMPT_RESULT_DIR
        self.reader = DataReader()
        
    def _write_to_file(self, content:str, filename: str):
        try:
            with open(filename, 'w') as file:
                file.write(content)
            self.logger.info(f"Data written to {filename}")
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
        
    def _extract_to_lists(self):
        
        newlines_questions = []
        newlines_answers = []
        for i, text in enumerate(self.questions):
            if len(text) == 0:
                newlines_questions.append(i)                    
        for i, text in enumerate(self.answers):
            if len(text) == 0:
                newlines_answers.append(i)
        
        queries = [query.strip() for query in self.queries if query.startswith("db.")]
        self.all_questions_list = []
        self.all_answers_list = []
        self.all_queries_list = []
        
        for query in queries:
            try:
                questions_index = next(i for i, q in enumerate(self.questions) if query.lower() in q.lower())
                answers_index = next(i for i, q in enumerate(self.answers) if query.lower() in q.lower())
            except StopIteration:
                self.logger.warning(f"No question found with query: {query}")
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
    
    def clean_prompt_output(self):
        # Delete all files in ERROR_FILES_DIR
        for filename in ERROR_FILES_DIR.iterdir():
            if filename.is_file():
                os.remove(filename)
        for file in os.listdir(PROMPT_RESULT_DIR):
            try:
                self.logger.info(f"\n\nPrompt output started processed for {file}")
                self.content = self.reader.read_prompt_output_file(file)
                
                self._seperate_sections()
                self._extract_to_lists()
                output_file = file.replace(".txt", ".csv")
                self._write_to_csv(OUTPUT_DIR / output_file, self.all_questions_list, self.all_answers_list, self.all_queries_list)
               
            except Exception as e:
                src = PROMPT_RESULT_DIR / file
                dest = ERROR_FILES_DIR / file
                import shutil
                shutil.copy(src, dest)
                self.logger.error(f"An unexpected error occurred during processing {file}: {e}")


if __name__ == "__main__":
    cleaner = DataCleaner()
    cleaner.clean_prompt_output()
