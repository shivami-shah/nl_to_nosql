import os
import logging
from project_logger import setup_logger

logger = setup_logger(os.getenv("LOG_LEVEL"))

def _write_to_output_file(content: str, filename: str, output_dir: str = "output"):
    """
    Writes the given content to a specified file within the output directory.

    Args:
        content (str): The text content to write to the file.
        filename (str): The name of the file (e.g., "queries.txt").
        output_dir (str): The name of the directory where the file will be saved.
                          Defaults to "output".
    Returns:
        bool: True if the file was written successfully, False otherwise.
    """
    try:
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, filename)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Successfully wrote content to '{file_path}'.")
        return True
    except IOError as e:
        logger.error(f"Error writing to file '{file_path}': {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred while writing to '{file_path}': {e}", exc_info=True)
        return False
    

def write_to_files(generated_queries: str,
                   generated_questions: str,
                   generated_answers: str,
                   file_prefix: str,
                   file_suffix: str) -> bool:
    """
    Example function to demonstrate writing to output files.
    This function can be modified to write different types of content.
    """
    status = _write_to_output_file(generated_queries, f"{file_prefix}_queries_{file_suffix}")
    if not status:
        logger.error("Failed to write generated queries to file.")
        return False

    status = _write_to_output_file(generated_questions, f"{file_prefix}_questions_{file_suffix}")
    if not status:
        logger.error("Failed to write generated questions to file.")
        return False

    status = _write_to_output_file(generated_answers, f"{file_prefix}_answers_{file_suffix}")
    if not status:
        logger.error("Failed to write generated answers to file.")
        return False
    
    return True


if __name__ == "__main__":
    print("--- Testing write_to_output_file function ---")

    text = "This is a test content for the output file."
    filename = "test_output.txt"
    # Write test data
    _write_to_output_file(text, filename)

    print("\nCheck the 'output' directory for 'test_output.txt'.")