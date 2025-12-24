# api/v1/match.py

from fastapi import APIRouter
from schemas.match_request import MatchRequest
from schemas.match_response import MatchResponse
from application.matcher_service import match_documents_v2
from mappers.keyword_mapper import to_domain_keywords
from mappers.match_mapper import to_match_responses
from typing import List

router = APIRouter()

@router.post("", response_model=List[MatchResponse])
async def match_v2(req: MatchRequest) -> List[MatchResponse]:
    domain_keywords = to_domain_keywords(req.keywords)
    matched_docs = await match_documents_v2(domain_keywords, req.language_code)
    return to_match_responses(matched_docs)
