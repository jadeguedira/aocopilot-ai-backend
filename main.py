# main.py

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from api.v1 import ask, analyze, match, match_v2, documents
from contextlib import asynccontextmanager
from infrastructure.lightrag_engine import init_rag

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_rag()  
    yield  # Let the app run
    # Later : maybe add cleanup here

app = FastAPI(lifespan=lifespan)

app.include_router(ask.router, prefix="/ask", tags=["RAG Queries"])
app.include_router(analyze.router, prefix="/analyze", tags=["Document Analysis"])
app.include_router(match.router, prefix="/match-mini", tags=["Match Requests"])
app.include_router(match_v2.router, prefix="/match", tags=["Match Requests"])
app.include_router(documents.router, prefix="/documents", tags=["Ingest"])

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)},
    )