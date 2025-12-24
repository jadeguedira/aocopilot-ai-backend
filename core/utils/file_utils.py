# infrastructure/file_utils.py

import base64
import tempfile
import os

def save_base64_to_tempfile(file_buffer: str, suffix=".pdf") -> str:
    """Decode base64 content into a temporary file. Returns the file path."""
    pdf_bytes = base64.b64decode(file_buffer)
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(pdf_bytes)
        return tmp.name

def cleanup_tempfile(path: str):
    """Delete a temporary file if it exists."""
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
