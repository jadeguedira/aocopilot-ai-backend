# scripts/analysis_test1.py

import base64
import requests
import os
import sys
import json

# Add project root to sys.path
script_dir = os.path.dirname(__file__) #  Gets the folder where the current script is located.
project_root = os.path.abspath(os.path.join(script_dir, "..")) # Moves one level up from that folder and gives the absolute path (i.e. the project root).
sys.path.append(project_root) #  Adds the project root to Python’s module search path

from infrastructure.logger import write_log, debug
from schemas.analysis_request import AnalysisRequest

# Script code
debug("Starting analysis_test1.py...")

# -> Replace with the file name you inserted in the scripts/data folder
file_name = "sample_document.pdf"

file_path = os.path.join(script_dir, "data", file_name)
with open(file_path, "rb") as f:
    encoded = base64.b64encode(f.read()).decode("utf-8")

write_log(f"Encoded file :{encoded}", header="File Encoding", file_name="file_encoding.log")

# Call the AI1 endpoint with the encoded file
language_code = 'en'
analysisRequest = AnalysisRequest(file_buffer=encoded, language_code=language_code)

endpointAI1 = "http://localhost:8001/analyze" #Correct with the correct endpoint

# Handle response
response = requests.post(endpointAI1, json=analysisRequest.model_dump())
print(f"Status code: {response.status_code}")

response_data = response.json()
response_str = json.dumps(response_data, indent=2)

print(response_str[:50]+'...')  # Print first 50 characters 
write_log(f"Encoded file :{response_str}", header="AI1 Result", file_name="AI1_results.log")

