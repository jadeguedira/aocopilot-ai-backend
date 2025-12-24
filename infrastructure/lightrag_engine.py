#infrastructure/lightrag_engine.py

import time
from lightrag import LightRAG
from infrastructure.embedder import embedder
from infrastructure.azure_llm import azure_llm
from infrastructure.logger import debug
from lightrag.kg.shared_storage import initialize_pipeline_status
import json

WORKDIR = "rag_storage"

_lightrag: LightRAG | None = None

async def init_rag() -> LightRAG:
    global _lightrag
    if _lightrag is None:
        # Initialize LightRAG
        start = time.time() 
        _lightrag = LightRAG(
            working_dir=WORKDIR,
            embedding_func=embedder,
            llm_model_func=azure_llm,
            chunk_token_size=99999,
        )
        await _lightrag.initialize_storages()
        await initialize_pipeline_status()
        debug(f"[INFO] Initialization complete in {time.time() - start:.2f}s")
    return _lightrag

async def query_similar_chunks_from_keywords(weighted_query: str, top_k: int = 30):
    return await _lightrag.chunks_vdb.query(weighted_query, top_k=top_k)

async def query_similar_chunks_from_keyword(keyword: str, top_k: int = 30):
    q = keyword.strip()
    if not q:
        return []
    return await _lightrag.chunks_vdb.query(keyword, top_k=top_k)

def get_slide_number(chunk_id, json_path="rag_storage/kv_store_text_chunks.json", default=-1):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if chunk_id not in data:
        return default

    return data[chunk_id].get("chunk_order_index", default)