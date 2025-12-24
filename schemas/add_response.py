# schemas/add_response.py

from pydantic import BaseModel

class AddResponse(BaseModel):
    success: str