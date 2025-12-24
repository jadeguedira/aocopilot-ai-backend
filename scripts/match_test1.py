# scripts/match_test1.py

import requests
import os
import sys
import json

script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.append(project_root)

from infrastructure.logger import write_log, debug
from schemas.match_request import MatchRequest
from schemas.keyword import Keyword
# Script code
debug("Starting match_test1.py...")

endpoint = "http://localhost:8001/match" #Correct with the correct endpoint

# 2. Prepare request data
language_code = 'en'
keywords = MatchRequest(
    keywords=[
        Keyword(keyword="java", score=2),
        Keyword(keyword="data", score=3)
    ],
    language_code=language_code
)

response = requests.post(endpoint, json=keywords.model_dump())
print(f"Status code: {response.status_code}")

# Handle response
response_data = response.json()
response_str = json.dumps(response_data, indent=2)

print(response_str[:100] + "...")  # Print first 100 chars
write_log(response_str, header="Match Response", file_name="match_results.log")
