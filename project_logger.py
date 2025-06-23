import logging
import os
from datetime import datetime

def setup_logger(level=logging.INFO):
    """
    Sets up a logger that outputs to a date-stamped file within a 'log_files' folder
    and also to the console.

    Args:
        level (int): The minimum logging level to capture (e.g., logging.INFO, logging.DEBUG, logging.ERROR).

    Returns:
        logging.Logger: The configured logger instance.
    """
    # Create a logger instance
    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    if not logger.handlers:
        
        log_dir = "log_files"
        os.makedirs(log_dir, exist_ok=True)

        today_date = datetime.now().strftime("%Y-%m-%d")
        log_file_name = f"log-{today_date}.log"
        log_file_path = os.path.join(log_dir, log_file_name) # Combine directory and file name

        # Create a file handler
        file_handler = logging.FileHandler(log_file_path, mode='a') # 'a' for append mode
        # Create a formatter for the file handler
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # --- Console Handler Setup ---
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO) # Console generally shows INFO and above
        # Create a formatter for the console handler
        console_formatter = logging.Formatter('%(levelname)s: %(message)s') # Simpler format for console
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger

# Example of how you might use it if run directly (for testing project_logger.py)
if __name__ == "__main__":
    test_logger = setup_logger(level=logging.DEBUG)
    test_logger.debug("This is a debug message.")
    test_logger.info("This is an info message.")
    test_logger.warning("This is a warning message.")
    test_logger.error("This is an error message.")
    test_logger.critical("This is a critical message.")
    try:
        raise ValueError("A test error occurred!")
    except ValueError:
        test_logger.exception("Exception in test block.")
    print(f"\nCheck the 'log_files' directory for the log file (e.g., log-{datetime.now().strftime('%Y-%m-%d')}.log) and your console for log messages.")