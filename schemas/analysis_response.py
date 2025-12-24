# schemas/analysis_response.py

from pydantic import BaseModel
from typing import List
from schemas.keyword import Keyword

class AnalysisResponse(BaseModel):
    summary: str
    keywords: List[Keyword]
