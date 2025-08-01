import time
from tenacity import RetryError
from APIManager import APIManager
from project_logger import setup_project_logger

class QueryGenerator:
    logger = setup_project_logger("QueryGenerator")
    
    def __init__(self):
        self.api_manager = APIManager()

    def send_chained_prompts_to_llm(
        self,
        prompt1_template: str,
        prompt2_template: str,
        prompt3_template: str,
        prompt4_template: str,
        delay_between_steps_seconds: int = 2
    ) -> str | None:
        """
        Sends prompt1, then uses its output in prompt2, prompt3 and prompt4.
        Includes delays and retries for each step.
        """
        self.logger.info("Starting chained LLM calls.")
        
        # --- Step 1: Call with prompt1_template ---
        self.logger.info("Calling LLM with Prompt 1: Queries Generation.")
        output_prompt1 = None
        try:
            output_prompt1 = self.api_manager.call_llm_api(prompt1_template)
            if not output_prompt1:
                self.logger.error("Prompt 1 call failed or returned no text.")
                return None
            self.logger.debug(f"Output from Prompt 1: {output_prompt1[:30]}...")
        except RetryError as e:
            self.logger.error(f"All retries failed for Prompt 1: {e}")
            return None
        except Exception as e:
            self.logger.critical(f"An unexpected error occurred during Prompt 1 call: {e}", exc_info=True)
            return None

        time.sleep(delay_between_steps_seconds)

        # --- Step 2: Call with prompt2_template, integrating output_prompt1 ---
        self.logger.info("Calling LLM with Prompt 2: Questions Generation.")
        prompt2_content = prompt2_template.replace("QUERIES", output_prompt1)
        output_prompt2 = None
        try:
            output_prompt2 = self.api_manager.call_llm_api(prompt2_content)
            if not output_prompt2:
                self.logger.error("Prompt 2 call failed or returned no text.")
                return None
            self.logger.debug(f"Output from Prompt 2: {output_prompt2[:30]}...")
        except RetryError as e:
            self.logger.error(f"All retries failed for Prompt 2: {e}")
            return None
        except Exception as e:
            self.logger.critical(f"An unexpected error occurred during Prompt 2 call: {e}", exc_info=True)
            return None
            
        time.sleep(delay_between_steps_seconds)

        # --- Step 3: Call with prompt3_template, integrating output_prompt1 ---
        self.logger.info("Calling LLM with Prompt 3: Search Term Generation.")
        prompt3_content = prompt3_template.replace("QUERIES", output_prompt1)
        output_prompt3 = None
        try:
            output_prompt3 = self.api_manager.call_llm_api(prompt3_content)
            if not output_prompt3:
                self.logger.error("Prompt 3 call failed or returned no text.")
                return None
            self.logger.debug(f"Final Output from Prompt 3: {output_prompt3[:30]}...")
        except RetryError as e:
            self.logger.error(f"All retries failed for Prompt 3: {e}")
            return None
        except Exception as e:
            self.logger.critical(f"An unexpected error occurred during Prompt 3 call: {e}", exc_info=True)
            return None
        
        # --- Step 4: Call with prompt4_template, integrating output_prompt1 ---
        self.logger.info("Calling LLM with Prompt 4: Answer Generation.")
        prompt4_content = prompt4_template.replace("QUERIES", output_prompt1)
        output_prompt4 = None
        try:
            output_prompt4 = self.api_manager.call_llm_api(prompt4_content)
            if not output_prompt4:
                self.logger.error("Prompt 4 call failed or returned no text.")
                return None
            self.logger.debug(f"Final Output from Prompt 4: {output_prompt4[:30]}...")
        except RetryError as e:
            self.logger.error(f"All retries failed for Prompt 4: {e}")
            return None
        except Exception as e:
            self.logger.critical(f"An unexpected error occurred during Prompt 4 call: {e}", exc_info=True)
            return None

        self.logger.info("Chained LLM calls completed successfully.")
        return output_prompt1, output_prompt2, output_prompt3, output_prompt4