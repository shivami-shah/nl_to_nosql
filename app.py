# app.py
import time
from config import DATA_DIR
from Orchestrator import Orchestrator

if __name__ == "__main__":
    # Ensure the directory exists
    DATA_DIR.mkdir(exist_ok=True)    
    orchestrator = Orchestrator()
    start_time = time.time()
    orchestrator.run_workflow()
    end_time = time.time()
    
    orchestrator.logger.info(f"Total workflow time: {end_time - start_time:.2f} seconds.")