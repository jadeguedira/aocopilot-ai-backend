# domain/document_ingestor.py
import fitz
from PIL import Image
from io import BytesIO
import base64
import json
import os
import hashlib
from infrastructure.azure_llm import azure_llm
from infrastructure.lightrag_engine import init_rag  
from infrastructure.logger import debug, write_log

SPLIT_MARKER = "====SPLIT===="
CUSTOM_SEPARATOR = f"\n\n{SPLIT_MARKER}\n\n"

slide_analysis_prompt = """ You are analyzing a slide from a professional Response to a Call for Tenders presentation.

Please return two sections:

---

### [Extracted Text]
Extract all visible text exactly as it appears on the slide.  
Preserve the wording, line breaks, bullet points, and labels.  
Do not summarize or paraphrase — just list what is visible.

---

### [Visual Summary]
Describe only the visual elements that contribute to the **meaning, structure, or interpretation** of the slide.  
Ignore purely decorative features (e.g., colors, white space, logos, branding).  
Focus only on layout, icons, diagrams, or formatting that affect how the content is understood.

Do not add interpretations, summaries, or opinions. Just describe the visual design.
"""

def pdf_slide_to_base64(pdf_path, page_number):
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)
    pix = page.get_pixmap(dpi=200)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

def get_cache_key(doc_id, slide_number):
    key = f"{doc_id}_slide_{slide_number}"
    return hashlib.md5(key.encode()).hexdigest()

def get_cache_path(cache_dir, key):
    return os.path.join(cache_dir, f"{key}.json")

# Send image to GPT-4o for captioning/summary
async def describe_slide_cached(
        image_base64: str,
        slide_number: int,
        doc_id: str = None,
        use_cache: bool = True,
        cache_dir="./gpt_cache"
        ) -> str:
    """
    Describe a slide image with optional caching.
    - If use_cache=True and doc_id is provided, results are cached.
    - If use_cache=False or no doc_id, always call the LLM without cache.
    """

    path = None

    if use_cache and doc_id:
        os.makedirs(cache_dir, exist_ok=True)
        key = get_cache_key(doc_id, slide_number)
        path = get_cache_path(cache_dir, key)

        # Return cached description if available
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)["description"]
    try:
        response = await azure_llm(slide_analysis_prompt, image_data=image_base64)
        # Save the response to cache
        if use_cache and doc_id and path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"description": response}, f)

    except Exception as e:
        debug(f"[ERROR] Failed to describe slide {slide_number} (doc={doc_id}): {e}")
        response = f"ERROR: LLM failed - {e}"

    return response

async def ingest_pdf_into_rag(pdf_path, doc_id, file_name) -> bool:
    """
    Try to ingest a PDF into LightRAG.
    Return True if it succeded, False otherwise.
    """
    try:
        lightrag = await init_rag()
        chunks = []

        with fitz.open(pdf_path) as doc:
            total_pages = len(doc)
            for idx, _ in enumerate(doc):
                slide_number = idx + 1
                try:
                    img_b64 = pdf_slide_to_base64(pdf_path, idx)
                    summary = await describe_slide_cached(img_b64, slide_number, doc_id)
                except Exception as e:
                    debug(f"[ERROR] Failed to process slide {slide_number} (doc={doc_id}): {e}")
                    continue  # skip this slide but continue others
                full_content = (
                    f"This is slide {slide_number} from the document '{file_name}'.\n\n{summary.strip()}"
                )
                chunks.append(full_content)

        # Case where no chunks are created
        if not chunks:
            debug(f"No chunks extracted for document {doc_id}")
            return False


        joined_text = CUSTOM_SEPARATOR.join(chunks)

        write_log(
            msg=joined_text,
            header='Added files',
            file_name='added_files.log'
        )

        try:
            await lightrag.ainsert(
                joined_text,
                split_by_character=SPLIT_MARKER,
                split_by_character_only=True,
                ids=[doc_id],
                file_paths=[file_name]
            )
        except Exception as e:
            debug(f"❌ Failed inserting document {doc_id} into LightRAG: {e}")
            return False

        debug(f"Ingested {total_pages} slides from '{doc_id}' into LightRAG.")
        return True

    except Exception as e:
        debug(f"❌ Unexpected error while ingesting {pdf_path}: {e}")
        return False