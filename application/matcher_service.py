# application/matcher_service.py

from domain.keyword import Keyword as DomainKeyword
from domain.matched_document import MatchedDocument
from typing import List, Dict, Tuple
import time
from infrastructure.logger import debug, write_log

from infrastructure.lightrag_engine import query_similar_chunks_from_keywords, get_slide_number
from infrastructure.azure_llm import ask_llm_for_ranked_documents
from domain.document import Document
from domain.chunk import Chunk


def _generate_weighted_query(keywords: List[DomainKeyword]) -> str:
    """
+    Build a token-weighted query by repeating each keyword token according to its integer weight.
+    """
    return " ".join(
        kw.keyword.lower() for kw in keywords for _ in range(kw.score)
    )


def _group_chunks_by_document(chunks_results) -> Dict[str, Document]:
    documents_by_ao = {}
    for raw_chunk in chunks_results: 
        doc_id = raw_chunk["full_doc_id"]
        chunk_id = raw_chunk["id"]
        chunk = Chunk(
            id=chunk_id,
            doc_id=doc_id,
            content=raw_chunk["content"],
            distance=raw_chunk["distance"],
            slide_number=get_slide_number(chunk_id)
        )
        documents_by_ao[doc_id] = documents_by_ao.get(doc_id, Document(ao_id=doc_id, chunks=[]))
        documents_by_ao[doc_id].add_chunk(chunk)
    return documents_by_ao


def _map_llm_result_to_matched_documents(
    llm_result,
    score_lookup
) -> List[MatchedDocument]:
    """
    Map LLM output to MatchedDocument domain objects.
    """
    matched_docs: List[MatchedDocument] = []
    for item in llm_result:
        ao_id = item.get("document")
        explanation = item.get("explanation", "")
        related_keywords = item.get("keywords", [])

        mk = [
            DomainKeyword(keyword=kw, score=score_lookup.get(kw.lower(), 0))
            for kw in related_keywords
            if kw and kw.lower() in score_lookup
        ]
        matched_docs.append(
            MatchedDocument(
                ao_id=ao_id,
                explanation=explanation,
                matched_keywords=mk
            )
        )
    return matched_docs


async def match_documents(keywords: List[DomainKeyword], language_code: str, top_k: int = 15) -> List[MatchedDocument]:
    start = time.time()

    # 1. Generate weighted query string
    weighted_query = _generate_weighted_query(keywords)

    # 2. Get chunks from vector database
    chunks_results = await query_similar_chunks_from_keywords(weighted_query, top_k)

    # 3. Group chunks by document -> instantiate Document objects
    documents_by_ao = _group_chunks_by_document(chunks_results)

    debug(f"[INFO] Found {len(documents_by_ao)} documents with {len(chunks_results)} chunks in total.")
    write_log(
        msg="\n".join([doc.get_chunks_preview_str() for doc in documents_by_ao.values()]),
        header=f'Documents Matching {weighted_query}',
        file_name="matched_documents.log",
    )

    # 4. Call LLM to rank documents
    documents = list(documents_by_ao.values())
    llm_result = await ask_llm_for_ranked_documents(keywords, documents, language_code)
    write_log(
        msg=f"{llm_result}",
        header="LLM Object Response",
        file_name="response_LLMs.log",
    )

    # 5. Create MatchedDocument objects
    score_lookup = {k.keyword.lower(): k.score for k in keywords}
    matched_docs = _map_llm_result_to_matched_documents(llm_result, score_lookup)

    debug(f"[INFO] Matching complete in {time.time() - start:.2f}s")
    return matched_docs


# Version 2 with improved scalability :

def _init_doc_acc(doc_id: str) -> Dict:
        return {
            "doc": Document(ao_id=doc_id, chunks=[]),
            "per_kw_best_sim": {},
            "evidence": [],
            "seen_chunks": set()
        }

def _process_chunk(
    doc_acc: Dict[str, Dict],
    doc_id: str,
    kw_lower: str,
    sim: float,
    chunk: Chunk
):
    """Processes a single chunk for a given document, updating the best similarity score for a keyword
    and collecting evidence chunks if it has not been seen before."""
    prev = doc_acc[doc_id]["per_kw_best_sim"].get(kw_lower, 0.0)
    if sim > prev:
        doc_acc[doc_id]["per_kw_best_sim"][kw_lower] = sim

    chunk_id = chunk.id
    if chunk_id not in doc_acc[doc_id]["seen_chunks"]:
        doc_acc[doc_id]["evidence"].append(chunk)
        doc_acc[doc_id]["seen_chunks"].add(chunk_id)

async def _gather_chunks_per_keyword(
    keywords: List[DomainKeyword],
    per_keyword_k: int,
) -> Dict[str, Dict]:
    """
    For each keyword, query similar chunks and aggregate them per document.
    Returns a dict: doc_id -> aggregation info.
    """
    
    doc_acc: Dict[str, Dict] = {}
    for kw in keywords:
        q = kw.keyword.strip()
        if not q:
            continue

        raw_chunks = await query_similar_chunks_from_keywords(q, top_k=per_keyword_k)

        for raw_chunk in raw_chunks:
            doc_id = raw_chunk["full_doc_id"]
            sim = raw_chunk["distance"]
            chunk_id = raw_chunk["id"]
            chunk = Chunk(
                id=chunk_id,
                doc_id=doc_id,
                content=raw_chunk["content"],
                distance=raw_chunk["distance"],
                slide_number=get_slide_number(chunk_id)
            )

            if doc_id not in doc_acc:
                doc_acc[doc_id] = _init_doc_acc(doc_id)

            kw_lower = kw.keyword.lower()
            _process_chunk(doc_acc, doc_id, kw_lower, sim, chunk)
    return doc_acc

# Scoring functions

def _normalize_similarity(sim: float, norm_min: float = 0.7, norm_max: float = 0.9) -> float:
    """
    Normalize a similarity score to the range [0, 1] based on provided minimum and maximum normalization bounds.

    Args:
        sim (float): The similarity score to normalize.
        norm_min (float, optional): The minimum similarity value for normalization. Defaults to 0.7.
        norm_max (float, optional): The maximum similarity value for normalization. Defaults to 0.9.

    Returns:
        float: The normalized similarity score in the range [0, 1].
    """
    scale = max(norm_max - norm_min, 1e-6)
    sim_norm = (sim - norm_min) / scale
    return 0.0 if sim_norm < 0 else (1.0 if sim_norm > 1 else sim_norm)

def _compute_doc_score(per_kw_best_sim: Dict[str, float], score_lookup: Dict[str, int]) -> Tuple[float, List[DomainKeyword]]:
    """
    Compute the total document score based on the best similarity per keyword and their weights.

    Args:
        per_kw_best_sim (Dict[str, float]): Mapping of keywords (lowercase) to their best similarity scores.
        score_lookup (Dict[str, int]): Mapping of keywords (lowercase) to their assigned weights.

    Returns:
        Tuple[float, List[DomainKeyword]]: The total computed score and a list of matched keywords with their scores.
    """
    total_score = 0.0
    matched_keywords: List[DomainKeyword] = []
    for kw_lower, best_sim in per_kw_best_sim.items():
        weight = score_lookup.get(kw_lower, 0)
        if weight <= 0 or best_sim <= 0:
            continue
        sim_norm = _normalize_similarity(best_sim)
        w_factor = 1.0 + 0.5 * (weight - 1)
        total_score += w_factor * sim_norm
        matched_keywords.append(DomainKeyword(keyword=kw_lower, score=weight))
    return total_score, matched_keywords

def _select_top_evidence(evidence: List[Chunk], per_doc_chunk_limit: int) -> List[Chunk]:
    """
    Selects the top evidence chunks based on their distance score.

    Args:
        evidence (List[Chunk]): List of evidence chunks to select from.
        per_doc_chunk_limit (int): Maximum number of chunks to select.

    Returns:
        List[Chunk]: The top evidence chunks sorted by distance in descending order.
    """
    evidence_sorted = sorted(evidence, key=lambda c: c.distance, reverse=True)
    return evidence_sorted[:per_doc_chunk_limit]

def _score_and_select_documents(
    doc_acc: Dict[str, Dict],
    score_lookup: Dict[str, int],
    per_doc_chunk_limit: int,
    docs_for_llm: int
) -> List[Tuple[str, float, List[DomainKeyword], List[Chunk]]]:
    """
    Score documents based on keyword matches and select top docs_for_llm documents.
    Returns a list of tuples: (doc_id, total_score, matched_keywords, evidence_top)
    """

    # 1. Aggregate scores and matched keywords for each document
    scored: List[Tuple[str, float, List[DomainKeyword], List[Chunk]]] = []
    for doc_id, agg in doc_acc.items():
        per_kw_best_sim: Dict[str, float] = agg["per_kw_best_sim"]
        evidence: List[Chunk] = agg["evidence"]

        # 2. Compute score and matched keywords
        total_score, matched_keywords = _compute_doc_score(per_kw_best_sim, score_lookup)
        if not matched_keywords:
            continue

        # 3. Select top evidence chunks for this document
        evidence_top = _select_top_evidence(evidence, per_doc_chunk_limit)
        scored.append((doc_id, total_score, matched_keywords, evidence_top))

    # 4. Sort documents by score and number of matched keywords
    scored.sort(key=lambda r: (r[1], len(r[2])), reverse=True)

    # 5. Return only the top docs_for_llm documents
    return scored[:docs_for_llm]


def _prepare_documents_for_llm(
    top_for_llm: List[Tuple[str, float, List[DomainKeyword], List[Chunk]]]
) -> List[Document]:
    """
    Prepare Document objects with only the evidence chunks for LLM input.
    """
    docs_for_llm_domain: List[Document] = []
    for doc_id, _, _, evidence in top_for_llm:
        d = Document(ao_id=doc_id, chunks=list(evidence))
        docs_for_llm_domain.append(d)
    return docs_for_llm_domain






async def match_documents_v2(
        keywords: List[DomainKeyword],
        language_code: str,
        *,
        per_keyword_k: int = 8,
        per_doc_chunk_limit: int = 6,
        docs_for_llm: int = 12,
        ) -> List[MatchedDocument]:
    """
    Second method with a pipeline that will work with a large dataset :
    Stage 1 (deterministic): gather chunks per keyword, aggregate per document,
    score docs by weighted best-sim per keyword, and keep only top docs_for_llm.
    Stage 2 (LLM): ask the LLM to re-rank those few docs and produce explanations.
    """
    start = time.time()
    score_lookup = {k.keyword.lower(): k.score for k in keywords}

    # 1. Gather chunks per keyword and aggregate per document
    doc_acc = await _gather_chunks_per_keyword(keywords, per_keyword_k)

    # 2. Score and select top documents for LLM
    top_for_llm = _score_and_select_documents(doc_acc, score_lookup, per_doc_chunk_limit, docs_for_llm)

    # 3. Prepare Document objects for LLM
    docs_for_llm_domain = _prepare_documents_for_llm(top_for_llm)

    # Print Log of the retrieved documents
    write_log(
        msg="\n".join([doc.get_chunks_preview_str() for doc in docs_for_llm_domain]),
        header=f'Documents Matching',
        file_name="matched_documents.log",
    )

    # 4. Ask LLM to re-rank these few docs + generate explanations and related keywords
    llm_result = await ask_llm_for_ranked_documents(keywords, docs_for_llm_domain, language_code)

    write_log(
        msg=f"{llm_result}",
        header="LLM Object Response (Top Docs Re-ranked)",
        file_name="response_LLMs.log",
    )

    # 5. Map LLM result -> domain MatchedDocument
    matched_docs = _map_llm_result_to_matched_documents(llm_result, score_lookup)

    total_chunks = sum(len(v["evidence"]) for v in doc_acc.values()) if doc_acc else 0
    debug(f"[INFO] Deterministic preselection: {len(top_for_llm)} docs sent to LLM, {total_chunks} raw chunks. Completed in {time.time() - start:.2f}s")

    return matched_docs