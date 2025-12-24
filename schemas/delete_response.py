# schemas/delete_response.py

from pydantic import BaseModel

class DeleteResponse(BaseModel):
    output: str