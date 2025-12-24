# application/analyzer_service.py

from infrastructure.analyzer_engine import summarize, extract_keywords
from schemas.analysis_response import AnalysisResponse, Keyword as KeywordSchema
from core.utils.file_loader import extract_text_from_buffer

import time
from infrastructure.logger import debug, write_log
    

async def analyze_text(file_buffer: str, language_code: str) -> AnalysisResponse: 
    start = time.time()

    document_text = extract_text_from_buffer(file_buffer)

    if not document_text:
        return AnalysisResponse(
            summary="ERROR: Could not extract text from PDF.",
            keywords=[]
        )

    summary = await summarize(document_text, language_code)
    domain_keywords = await extract_keywords(document_text)
    
    response_keywords = [
        KeywordSchema(keyword=k.keyword, score=k.score)
        for k in domain_keywords
    ]

    write_log(msg=f"Summary: {summary}\nKeywords: {[(k.keyword, k.score) for k in domain_keywords]}",
              header='AI1 Results', file_name="AI1_results.log")

    debug(f"[INFO] Analysis complete in {time.time() - start:.2f}s")

    return AnalysisResponse(summary=summary, keywords=response_keywords)
