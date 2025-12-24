# scripts/ask_test1.py

import requests
import os
import sys
import json

script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.append(project_root)

from infrastructure.logger import write_log, debug
from schemas.prompt import Prompt

# Script code
debug("Starting ask_test1.py...")

query_text = "What is the planning for the sample project?"
prompt = Prompt(query=query_text)

endpoint = "http://localhost:8001/ask" #Correct with the correct endpoint

response = requests.post(endpoint, json=prompt.model_dump())
print(f"Status code: {response.status_code}")

# Handle response
response_data = response.json()
response_str = json.dumps(response_data, indent=2)

print(response_str[:100] + "...")  # Print first 100 chars
write_log(response_str, header="Ask Response", file_name="ask_results.log")
