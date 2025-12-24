#api/v1/ask.py

from fastapi import APIRouter
from schemas.prompt import Prompt
from schemas.ask_response import AskResponse
from application.query_service import run_rag_query

router = APIRouter()

@router.post("")
async def ask_ai(prompt: Prompt) -> AskResponse:
    response = await run_rag_query(prompt.query)
    return response