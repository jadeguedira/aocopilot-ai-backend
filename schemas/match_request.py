# schemas/match_request.py

from pydantic import BaseModel
from typing import List
from schemas.keyword import Keyword

class MatchRequest(BaseModel):
    keywords: List[Keyword]
    language_code: str