# application/document_service.py

import time
from infrastructure.logger import debug, write_log
from core.utils.file_utils import save_base64_to_tempfile, cleanup_tempfile
from domain.document_ingestor import ingest_pdf_into_rag
from domain.document_deleter import remove_doc_from_rag 

async def add_document(doc_id: str, file_name: str, file_buffer: str) -> bool:
    """
    Adds a base64-encoded PDF document into the RAG pipeline.
    Returns True if successful, False otherwise.
    """
    start = time.time()

    success = False

    debug("[INFO] Starting ingestion pipeline...")
    
    # Decode base64 -> temp PDF
    tmp_path = save_base64_to_tempfile(file_buffer, suffix=".pdf")

    try:
        success = await ingest_pdf_into_rag(tmp_path, doc_id, file_name)
        debug(f"[INFO] Adding complete in {time.time() - start:.2f}s")
    except Exception as e:
        debug(f"[ERROR] Exception while ingesting {doc_id}: {e}")
        success = False
    finally:
        cleanup_tempfile(tmp_path)
        write_log(
            msg=f"Document {doc_id} ingestion {'succeeded' if success else 'failed'}.",
            header='Ingestion Results',
            file_name='ingestion_documents.log'
        )
        if success:
            debug(f"[INFO] Document {doc_id} ingested successfully")
        else:
            debug(f"[WARN] Document {doc_id} ingestion failed")
        
        
    return success

async def delete_document(doc_id: str) -> str:
    """
    Delete a document from LightRAG.
    Returns a message associated to the success.
    """
    start = time.time()
    debug(f"[INFO] Starting deletion for {doc_id}...")

    try:
        deletion_result = await remove_doc_from_rag(doc_id)

        if deletion_result.status == "success":
            debug(f"[INFO] Document {doc_id} deleted successfully")
            debug(f"[INFO] Deletion complete in {time.time() - start:.2f}s")
            return "success"
        elif deletion_result.status == "not_found":
            debug(f"[WARN] Document {doc_id} not found")
            return "not_found"
        else:
            debug(f"[ERROR] Failed to delete {doc_id}: {deletion_result.message}")
            return "failed"
    
    except Exception as e:
        debug(f"[ERROR] Unexpected error during deletion of {doc_id}: {e}")
        return "failed"

    finally:
        write_log(
            msg=f"Document {doc_id} deletion attempt resulted in: {deletion_result.status if 'deletion_result' in locals() else 'error'}.",
            header='Deletion Results',
            file_name='deletion_documents.log'
        )