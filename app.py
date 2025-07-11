# app.py
import time
from config import DATA_DIR
from Orchestrator import Orchestrator

if __name__ == "__main__":
    # Ensure the directories exist
    DATA_DIR.mkdir(exist_ok=True)    
    orchestrator = Orchestrator()
    start_time = time.time()
    orchestrator.run_workflow() # Call run_workflow without expecting a direct return of results here
    end_time = time.time()
    
    orchestrator.logger.info(f"Total workflow time: {end_time - start_time:.2f} seconds.")