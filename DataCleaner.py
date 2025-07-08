import csv
import os
from config import PROMPT_RESULT_DIR, OUTPUT_DIR
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
            
    def _write_to_csv(self, filename: str, list1:list, list2:list, list3:list):
        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Question", "Answer", "Query"])  # header row
                for row in zip(list1, list2, list3):
                    writer.writerow(row)
            self.logger.info(f"Data written to {filename}")                
        except Exception as e:
            self.logger.error(f"Failed to write data to {filename}: {str(e)}")

    def write_prompt_output(self, collection_name: str, query_type:str, output: str):
        query_type = ''.join(filter(str.isalpha, query_type))
        file_name = PROMPT_RESULT_DIR / f"{collection_name}_{query_type}.txt"
        self._write_to_file(output, file_name)
        
    def clean_prompt_output(self):        
        for file in os.listdir(PROMPT_RESULT_DIR):
            content = self.reader.read_prompt_output_file(file)
            
            queries_end_index = content.index("QUESTIONS")
            questions_end_index = content.index("ANSWERS")            
            queries = content[:queries_end_index].split('\n')
            questions = content[queries_end_index:questions_end_index].split('\n')[1:]
            answers = content[questions_end_index:].split('\n')[1:]
            
            newlines_questions = []
            newlines_answers = []
            for i, text in enumerate(questions):
                if len(text) == 0:
                    newlines_questions.append(i)                    
            for i, text in enumerate(answers):
                if len(text) == 0:
                    newlines_answers.append(i)
            
            queries = [query.strip() for query in queries if query.startswith("db.")]
            all_questions_list = []
            all_answers_list = []
            all_queries_list = []
            
            for query in queries:
                try:
                    questions_index = next(i for i, q in enumerate(questions) if query.lower() in q.lower())
                    answers_index = next(i for i, q in enumerate(answers) if query.lower() in q.lower())
                except StopIteration:
                    self.logger.warning(f"No question found with query: {query}")
                    
                questions_list = []
                answers_list = []
                
                temp_indexes = [i for i in newlines_questions if i > questions_index]
                next_question_index = min(temp_indexes) if temp_indexes else len(questions)-1
                temp_indexes = [i for i in newlines_answers if i > answers_index]
                next_answer_index = min(temp_indexes) if temp_indexes else len(answers)-1
                
                questions_list = questions[questions_index:next_question_index]
                answers_list = answers[answers_index:next_answer_index]
                
                questions_list = [q for q in questions_list if query not in q]
                questions_list = [q for q in questions_list if "Natural Language Questions" not in q]
                questions_list = [q for q in questions_list if "```" not in q]
                questions_list = [q.replace("*", "").strip() for q in questions_list]

                questions_list_append = ([c.split(":")[1].strip() for c in answers_list if "Question" in c])
                questions_list += questions_list_append
                
                answers_list = [c.split(":")[1].strip() for c in answers_list if "Answer" in c]
                
                extra_questions = len(questions_list) - len(answers_list)
                answers_list_extra = [answers_list[0]] * extra_questions
                answers_list += answers_list_extra
                
                query_list = [query]*len(questions_list)
                
                all_questions_list += questions_list
                all_answers_list += answers_list
                all_queries_list += query_list
                
            file = file.replace(".txt", ".csv")
            self._write_to_csv(filename=OUTPUT_DIR / file, list1=all_questions_list, list2=all_answers_list, list3=all_queries_list)

if __name__ == "__main__":
    cleaner = DataCleaner()
    cleaner.clean_prompt_output()
