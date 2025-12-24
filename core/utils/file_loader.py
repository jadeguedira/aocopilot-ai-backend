# infrastructure/file_loader.py

import base64
import fitz  # PyMuPDF
from typing import Optional
#from io import BytesIO
from infrastructure.logger import debug, write_log

def extract_text_from_buffer(file_buffer: str) -> Optional[str]:
    debug(f"Beginning text extraction...")
    try:
        # Step 1: decode base64 to bytes
        file_bytes = base64.b64decode(file_buffer)

        # Step 2: open as PDF in memory
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            all_text = "\n".join(page.get_text() for page in doc)
        
        write_log(f"Extracted text: {(all_text)}", header="Text Extraction", file_name="text_extraction.log")
        debug(f"[INFO] Text extraction complete, {len(all_text)} characters extracted.")
        
        return all_text
    except Exception as e:
        debug(f"[ERROR] Failed to extract text from file buffer: {e}")
        return None
