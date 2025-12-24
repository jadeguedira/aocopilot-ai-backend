# mappers/match_mapper.py

from typing import List
from domain.matched_document import MatchedDocument
from schemas.match_response import MatchResponse
from schemas.keyword import Keyword as SchemaKeyword

def to_match_responses(domain_docs: List[MatchedDocument]) -> List[MatchResponse]:
    return [
        MatchResponse(
            ao_id=doc.ao_id,
            explanation=doc.explanation,
            matched_keywords=[
                SchemaKeyword(keyword=kw.keyword, score=kw.score)
                for kw in doc.matched_keywords
            ]
        )
        for doc in domain_docs
    ]
