# domain/document.py

from dataclasses import dataclass, field
from typing import List, Optional
from domain.chunk import Chunk

@dataclass
class Document:
    ao_id: str
    chunks: List[Chunk] = field(default_factory=list)
    text: Optional[str] = None

    def add_chunk(self, chunk: Chunk) -> None:
        self.chunks.append(chunk)
    
    def get_chunks_preview_str(self, preview_length: int = 80) -> str:
        """
        Print a preview for all chunks in this document.
        """
        res = f"\nDocument: {self.ao_id}\n"
        if not self.chunks:
            res += "  (No chunks available)"
            return res

        for i, chunk in enumerate(self.chunks, start=1):
            res += f"{i} - {chunk.get_preview_str(preview_length)}\n'"
        return res
    