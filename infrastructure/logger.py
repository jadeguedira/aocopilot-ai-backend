#services/logger.py

import os
from dotenv import load_dotenv
from datetime import datetime

# Load .env variables
load_dotenv(dotenv_path=".env", override=True)

# Debug mode toggle
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
if DEBUG_MODE:
    print("[DEBUG] Debug mode is enabled")

def debug(msg: str):
    if DEBUG_MODE:
        print(f"[DEBUG] {msg}")

def write_log(msg: str, header: str = "", file_name: str = "app.log"):
    if DEBUG_MODE:
        script_dir = os.path.dirname(__file__)
        logs_dir = os.path.abspath(os.path.join(script_dir, "../logs"))
        os.makedirs(logs_dir, exist_ok=True)  # Ensure logs folder exists

        logfile_path = os.path.join(logs_dir, file_name)
        with open(logfile_path, "a", encoding="utf-8") as f:
            f.write(f"\n=== {header} ===\n")
            f.write(f"{datetime.now()}:\n{msg}\n\n{'='*40}\n")
        
        print(f"[LOG ADDED IN {file_name} - {header}] : {msg[:50]}...") 