from infrastructure.lightrag_engine import init_rag

async def remove_doc_from_rag(doc_id: str) -> bool:
    lightrag = await init_rag()
    return await lightrag.adelete_by_doc_id(doc_id)