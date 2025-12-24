# api/v1/analyze.py

from fastapi import APIRouter
from schemas.analysis_request import AnalysisRequest
from schemas.analysis_response import AnalysisResponse
from application.analyzer_service import analyze_text

router = APIRouter()

@router.post("", response_model=AnalysisResponse)
async def analyze(req: AnalysisRequest) -> AnalysisResponse:
    return await analyze_text(req.file_buffer, req.language_code)
