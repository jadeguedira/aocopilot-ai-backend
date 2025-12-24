# schemas/match_response.py

from pydantic import BaseModel
from typing import List
from schemas.keyword import Keyword

class MatchResponse(BaseModel):
    ao_id: str
    explanation: str
    matched_keywords: List[Keyword]
