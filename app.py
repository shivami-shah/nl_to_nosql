# app.py
from project_logger import setup_project_logger
from QueryGenerator import QueryGenerator
from APIManager import APIManager
from DataCleaner import DataCleaner
import os # Added for saving results

class Orchestrator:
    logger = setup_project_logger("Orchestrator")

    def __init__(self):
        self.query_generator = QueryGenerator()
        self.api_manager = APIManager()
        self.data_cleaner = DataCleaner()

    def run_workflow(self):
        self.logger.info("Starting LLM project workflow...")

        # 1. Generate all prompt templates
        self.logger.info("Generating chained prompt templates...")
        all_template_sets = self.query_generator.generate_queries()
        self.logger.info(f"Finished generating {len(all_template_sets)} sets of chained prompt templates.")

        final_cleaned_results = []

        for i, template_set in enumerate(all_template_sets):
            collection_name = template_set["collection"]
            query_type = template_set["query_type"]
            prompt1_template = template_set["prompt1"]
            prompt2_template = template_set["prompt2"]
            prompt3_template = template_set["prompt3"]

            self.logger.info(f"--- Processing combination {i+1}/{len(all_template_sets)}: "
                             f"Collection: {collection_name}, query_type: {query_type}")

            # 2. Send chained prompts to LLM and get final response
            output_prompt1, output_prompt2, output_prompt3 = self.api_manager.send_chained_prompts_to_llm(
                prompt1_template,
                prompt2_template,
                prompt3_template,
                delay_between_steps_seconds=2 # Adjust delay as needed
            )
            
            output = output_prompt1 + output_prompt2 + output_prompt3
            self.data_cleaner.write_to_text(collection_name, query_type, output)
            self.logger.info(f"--- Finished processing combination {i+1}/{len(all_template_sets)}")
            
            # Add an overall delay between processing each full chained set for different combinations
            if i < len(all_template_sets) - 1:
                self.logger.info(f"Pausing for 2 seconds before starting next combination's chained calls.")
                time.sleep(2) # Adjust as needed for overall rate limiting if many combinations

        self.logger.info("LLM project workflow completed.")
        return final_cleaned_results

if __name__ == "__main__":
    import time # Ensure time is imported if using sleep in main for testing
    orchestrator = Orchestrator()
    start_time = time.time()
    all_final_results = orchestrator.run_workflow()
    end_time = time.time()
    
    orchestrator.logger.info(f"Total workflow time: {end_time - start_time:.2f} seconds.")