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
    def call_llm_api(self, prompt_content: str):
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
