# domain/matched_document.py

from typing import List
from domain.keyword import Keyword

class MatchedDocument:
    def __init__(self, ao_id: str, explanation: str, matched_keywords: List[Keyword]):
        self.ao_id = ao_id
        self.explanation = explanation
        self.matched_keywords = matched_keywords
