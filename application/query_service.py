#application/query_service.py

from infrastructure.lightrag_engine import init_rag
from lightrag import QueryParam
import time
from infrastructure.logger import debug
from schemas.ask_response import AskResponse

async def run_rag_query(user_query: str) -> AskResponse:
    start = time.time()
    lightrag = await init_rag()

    param = QueryParam(mode='hybrid', top_k=15)
    result = await lightrag.aquery(user_query, param=param)
    debug(f"[INFO] Query complete in {time.time() - start:.2f}s")

    answer = result if result else "No relevant answer found."
    return AskResponse(answer=answer)
