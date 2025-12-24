# api/v1/documents.py

from fastapi import APIRouter
from schemas.add_request import AddRequest 
from schemas.add_response import AddResponse
from schemas.delete_response import DeleteResponse
from schemas.delete_request import DeleteRequest
from application.document_service import add_document, delete_document
from typing import List
import requests

router = APIRouter()

@router.post("", response_model=AddResponse)
async def add(req: AddRequest) -> AddResponse:
    success = await add_document(req.doc_id, req.file_name, req.file_buffer)
    result = "success" if success else "failed"
    return AddResponse(success=result)

@router.delete("/{doc_id}", response_model=DeleteResponse)
async def delete(req: DeleteRequest) -> DeleteResponse:
    result = await delete_document(req.doc_id)
    return DeleteResponse(output=result)