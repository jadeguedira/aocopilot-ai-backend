# domain/chunk.py

from dataclasses import dataclass

@dataclass
class Chunk:
    id: str
    content: str
    doc_id: str
    distance: float  # cosine similarity (the higher, the better)
    slide_number: int

    def get_preview_str(self, preview_length: int = 80) -> str:
        """
        Return a short, single-line preview of this chunk's content
        with similarity score.
        """
        preview = self.content.strip().replace("\n", " ")
        if len(preview) > preview_length:
            preview = preview[:preview_length] + "..."
        return f"Chunk {self.id} (slide={self.slide_number} ,score={self.distance:.4f}) : {preview}"