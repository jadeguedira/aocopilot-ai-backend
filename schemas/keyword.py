# schemas/keyword.py

from pydantic import BaseModel

class Keyword(BaseModel):
    keyword: str
    score: int