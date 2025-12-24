from pydantic import BaseModel 

# Python class that lets you define data models with validation and type checking
class Prompt(BaseModel):
    query: str