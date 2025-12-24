# schemas/analysis_request.py

from pydantic import BaseModel

class AnalysisRequest(BaseModel):
    file_buffer: str
    language_code: str
