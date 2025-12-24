# schemas/add_request.py

from pydantic import BaseModel

class AddRequest(BaseModel):
    file_buffer: str
    doc_id: str
    file_name: str