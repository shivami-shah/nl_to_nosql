import time
from google import genai
from project_logger import setup_project_logger
from config import API_KEY, EXTERNAL_MODEL # Import API_KEY and EXTERNAL_MODEL from config
from tenacity import retry, wait_exponential, stop_after_attempt, RetryError

class APIManager:
    logger = setup_project_logger("APIManager")

    def __init__(self):
        self.api_key = API_KEY
        self.model_name = EXTERNAL_MODEL
        if not self.api_key:
            self.logger.error("API_KEY not found in environment variables. Please set it in your .env file.")
            raise ValueError("API_KEY is not set.")
        try:
            self.client = genai.Client(api_key=self.api_key)
            self.logger.info(f"GenAI model '{self.model_name}' loaded successfully.")
        except Exception as e:
            self.logger.critical(f"Failed to initialize GenAI model '{self.model_name}': {e}")
            raise

    @retry(
        wait=wait_exponential(multiplier=1, min=4, max=60), # Wait 2^x * multiplier seconds between retries, max 60s
        stop=stop_after_attempt(5), # Stop after 5 attempts
        reraise=True # Re-raise the last exception if all retries fail
    )
    def _call_llm_api(self, prompt_content: str):
        """
        Internal method to make a single LLM API call with retry logic.
        This method is decorated with tenacity for automatic retries.
        """
        self.logger.info(f"Attempting to call GenAI with model: {self.model_name}")
        try:
            # response = self.client.generate_content(
            #     contents=prompt_content,
            # )
            response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt_content,
            )
            self.logger.info("Successfully received response from GenAI API.")
            if response and response.text:
                return response.text
            else:
                self.logger.warning("GenAI API call returned no text content.")
                raise RetryError("No text content in GenAI response, retrying...")
        except Exception as e:
            self.logger.error(f"Error calling GenAI API: {e}", exc_info=True)
            raise RetryError(f"GenAI API call failed: {e}") from e


    def send_chained_prompts_to_llm(
        self,
        prompt1_template: str,
        prompt2_template: str,
        prompt3_template: str,
        delay_between_steps_seconds: int = 2
    ) -> str | None:
        """
        Sends prompt1, then uses its output in prompt2, then uses prompt2's output in prompt3.
        Includes delays and retries for each step.
        """
        self.logger.info("Starting chained LLM calls.")
        
        # --- Step 1: Call with prompt1_template ---
        self.logger.info("Calling LLM with Prompt 1.")
        output_prompt1 = None
        try:
            output_prompt1 = self._call_llm_api(prompt1_template)
            if not output_prompt1:
                self.logger.error("Prompt 1 call failed or returned no text.")
                return None
            self.logger.debug(f"Output from Prompt 1: {output_prompt1[:100]}...") # Log first 100 chars
        except RetryError as e:
            self.logger.error(f"All retries failed for Prompt 1: {e}")
            return None
        except Exception as e:
            self.logger.critical(f"An unexpected error occurred during Prompt 1 call: {e}", exc_info=True)
            return None

        time.sleep(delay_between_steps_seconds) # Delay before next step

        # --- Step 2: Call with prompt2_template, integrating output_prompt1 ---
        self.logger.info("Calling LLM with Prompt 2 (integrating Prompt 1 output).")
        prompt2_content = prompt2_template.replace("QUERIES", output_prompt1)
        output_prompt2 = None
        try:
            output_prompt2 = self._call_llm_api(prompt2_content)
            if not output_prompt2:
                self.logger.error("Prompt 2 call failed or returned no text.")
                return None
            self.logger.debug(f"Output from Prompt 2: {output_prompt2[:100]}...") # Log first 100 chars
        except RetryError as e:
            self.logger.error(f"All retries failed for Prompt 2: {e}")
            return None
        except Exception as e:
            self.logger.critical(f"An unexpected error occurred during Prompt 2 call: {e}", exc_info=True)
            return None
            
        time.sleep(delay_between_steps_seconds) # Delay before next step

        # --- Step 3: Call with prompt3_template, integrating output_prompt2 ---
        self.logger.info("Calling LLM with Prompt 3 (integrating Prompt 1 output).")
        prompt3_content = prompt3_template.replace("QUERIES", output_prompt1)
        final_output = None
        try:
            output_prompt3 = self._call_llm_api(prompt3_content)
            if not output_prompt3:
                self.logger.error("Prompt 3 call failed or returned no text.")
                return None
            self.logger.debug(f"Final Output from Prompt 3: {output_prompt3[:100]}...") # Log first 100 chars
        except RetryError as e:
            self.logger.error(f"All retries failed for Prompt 3: {e}")
            return None
        except Exception as e:
            self.logger.critical(f"An unexpected error occurred during Prompt 3 call: {e}", exc_info=True)
            return None

        self.logger.info("Chained LLM calls completed successfully.")
        return output_prompt1, output_prompt2, output_prompt3