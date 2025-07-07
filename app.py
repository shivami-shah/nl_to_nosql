# app.py
import time
import os
import concurrent.futures
from tenacity import RetryError
from project_logger import setup_project_logger
from PromptGenerator import PromptGenerator
from QueryGenerator import QueryGenerator
from DataCleaner import DataCleaner
from config import MAX_WORKERS

class Orchestrator:
    logger = setup_project_logger("Orchestrator")

    def __init__(self):
        self.prompt_generator = PromptGenerator()
        self.query_generator = QueryGenerator()
        self.data_cleaner = DataCleaner()

    def _process_single_prompt_set(self, prompt_set: dict):
        """
        Helper method to process a single prompt set, including chained LLM calls
        and data writing. Designed to be run concurrently.
        """
        collection_name = prompt_set["collection"]
        query_type = prompt_set["query_type"]
        prompt1 = prompt_set["prompt1"]
        prompt2 = prompt_set["prompt2"]
        prompt3 = prompt_set["prompt3"]

        log_prefix = f"Collection: {collection_name}, Query Type: {query_type}"
        self.logger.info(f"--- Starting processing for {log_prefix}")

        try:
            # 2. Send chained prompts to LLM and get final response
            output_prompt1, output_prompt2, output_prompt3 = self.query_generator.send_chained_prompts_to_llm(
                prompt1, prompt2, prompt3,
                delay_between_steps_seconds=2 # Adjust delay as needed
            )
            
            if output_prompt1 and output_prompt2 and output_prompt3:
                output = f"QUERIES:\n{output_prompt1}\nQUESTIONS:\n{output_prompt2}\nANSWERS:\n{output_prompt3}"
                self.data_cleaner.write_to_text(collection_name, query_type, output)
                self.logger.info(f"--- Finished processing and data written for {log_prefix}")
                return True
            else:
                self.logger.error(f"One or more chained prompt calls failed for {log_prefix}. Skipping data write.")
                return False

        except RetryError as e:
            self.logger.error(f"All retries failed for {log_prefix}: {e}")
            return False
        except Exception as e:
            self.logger.critical(f"An unexpected error occurred during processing {log_prefix}: {e}", exc_info=True)
            return False

    def run_workflow(self):
        self.logger.info("Starting LLM project workflow...")

        # 1. Generate all prompt sets
        self.logger.info("Generating chained prompt templates...")
        all_prompt_sets = self.prompt_generator.generate_prompts()
        self.logger.info(f"Finished generating {len(all_prompt_sets)} sets of chained prompt templates.")

        # 2. Process each prompt set
        processed_count = 0
        successful_count = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Submit each prompt set processing to the executor
            future_to_prompt_set = {executor.submit(self._process_single_prompt_set, prompt_set): prompt_set for prompt_set in all_prompt_sets}

            for future in concurrent.futures.as_completed(future_to_prompt_set):
                prompt_set = future_to_prompt_set[future]
                collection_name = prompt_set["collection"]
                query_type = prompt_set["query_type"]
                processed_count += 1
                try:
                    success = future.result()
                    if success:
                        successful_count += 1
                except Exception as exc:
                    self.logger.error(f"Processing for {collection_name}-{query_type} generated an exception: {exc}")
                
                self.logger.info(f"--- Progress: {processed_count}/{len(all_prompt_sets)} sets processed. ({successful_count} successful)")
                
        self.logger.info(f"LLM project workflow completed. {successful_count} out of {len(all_prompt_sets)} prompt sets processed successfully.")
        return True

if __name__ == "__main__":
    orchestrator = Orchestrator()
    start_time = time.time()
    orchestrator.run_workflow() # Call run_workflow without expecting a direct return of results here
    end_time = time.time()
    
    orchestrator.logger.info(f"Total workflow time: {end_time - start_time:.2f} seconds.")