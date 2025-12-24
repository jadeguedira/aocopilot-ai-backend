# scripts/add_test1.py

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
from schemas.add_request import AddRequest

# Script code
debug("Starting add_test1.py...")

# -> Replace with the file name you inserted in the scripts/data folder
file_name = "sample_document.pdf"

file_path = os.path.join(script_dir, "data", file_name)
with open(file_path, "rb") as f:
    encoded = base64.b64encode(f.read()).decode("utf-8")

write_log(f"Encoded file :{encoded}", header="File Encoding", file_name="file_encoding.log")

# Call the add endpoint with the encoded file
doc_id = "test-document-001"
file_name = "Sample Document"
addRequest = AddRequest(file_buffer=encoded, doc_id=doc_id, file_name=file_name)

endpoint = "http://localhost:8001/documents" #Correct with the correct endpoint

# Handle response
response = requests.post(endpoint, json=addRequest.model_dump())
print(f"Status code: {response.status_code}")

response_data = response.json()
response_str = json.dumps(response_data, indent=2)

print(response_str[:50]+'...')  # Print first 50 characters 
write_log(f"Encoded file :{response_str}", header="Add Result", file_name="Add_results.log")