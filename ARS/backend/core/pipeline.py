"""
core/pipeline.py
Ports Notebook Module 13.
Orchestrates the full ARS pipeline end-to-end.
Also exposes get_or_rebuild_retriever() used by the chat API endpoint
to reconstruct a retriever for cached reports without re-running the pipeline.
"""
import os
import re
import time
import shutil
from typing import Dict, Optional

from core.config import CHROMA_PERSIST_DIR
from core.ingestion import extract_and_preprocess, chunk_document
from core.vectorstore import load_or_create_vectorstore, get_embedding_model
from core.retriever import build_ensemble_retriever
from core.summarizer import summarize_all_sections, save_summaries, load_summaries
from core.chat import save_chunks, load_chunks, start_chat_session


USE_DENSE_RETRIEVAL = os.getenv("ARS_USE_DENSE_RETRIEVAL", "false").lower() == "true"


def run_ars_pipeline(
    pdf_path: str,
    company: str,
    year: str,
    force_reindex: bool = False,
    force_resummarize: bool = False,
) -> Dict:
    """
    Full ARS pipeline: PDF → Extract → Chunk → Embed → Retrieve → Summarize.

    Args:
        pdf_path:           Absolute path to the annual report PDF
        company:            Company name (e.g., 'Infosys')
        year:               Report year as string (e.g., '2024')
        force_reindex:      Re-embeds from scratch even if vector cache exists (slow)
        force_resummarize:  Re-runs summarization using cached vectors (fast)
                            Use when you update prompts or fix summary errors.

    Returns:
        {
            "summaries":   {section_key: summary_text},
            "session_key": str,
            "from_cache":  bool
        }
    """

    # ── FAST PATH: summaries already cached and no force flags ──
    if not force_reindex and not force_resummarize:
        cached = load_summaries(company, year)
        if cached:
            # Rebuild retriever from disk for chat
            retriever = get_or_rebuild_retriever(company, year)
            if retriever:
                start_chat_session(company, year, retriever)
            return {
                "summaries":   cached["summaries"],
                "session_key": _make_session_key(company, year),
                "from_cache":  True,
            }

    # ── STEP 1: Extract & preprocess PDF ──
    pages = extract_and_preprocess(pdf_path)

    # ── STEP 2: Chunk ──
    chunks = chunk_document(pages)

    # ── STEP 3/4: Build retriever (dense+bm25 or stable bm25-only mode) ──
    if USE_DENSE_RETRIEVAL:
        if force_reindex:
            collection_name = re.sub(r'[^a-z0-9]+', '_', company.lower().strip())
            collection_path = os.path.join(CHROMA_PERSIST_DIR, f"ars_{collection_name}_{year}")
            if os.path.isdir(collection_path):
                shutil.rmtree(collection_path, ignore_errors=True)

        embed_model = get_embedding_model()
        vectorstore, _ = load_or_create_vectorstore(
            company, year,
            chunks=chunks,
            embedding_model=embed_model,
            force_recreate=force_reindex,
        )
        retriever = build_ensemble_retriever(vectorstore, chunks, k=15, use_dense=True)
    else:
        retriever = build_ensemble_retriever(None, chunks, k=15, use_dense=False)

    # ── STEP 5: Save chunks to disk (enables BM25 rebuild on future cached loads) ──
    save_chunks(chunks, company, year)

    # ── STEP 6: Summarize all sections in parallel ──
    summaries = summarize_all_sections(retriever)

    # ── STEP 7: Save summaries ──
    save_summaries(summaries, company, year)

    # ── STEP 8: Start chat session ──
    session_key = start_chat_session(company, year, retriever)

    return {
        "summaries":   summaries,
        "session_key": session_key,
        "from_cache":  False,
    }


def get_or_rebuild_retriever(company: str, year: str):
    """
    Rebuilds a retriever from cached vectorstore + chunks without re-running the pipeline.
    Used by the chat API endpoint to initialize sessions on-demand.

    Returns:
        HybridEnsembleRetriever if both vector cache and chunks exist,
        Dense-only retriever if only vector cache exists,
        None if no vector cache found at all.
    """
    saved_chunks = load_chunks(company, year)

    if not USE_DENSE_RETRIEVAL:
        if saved_chunks:
            return build_ensemble_retriever(None, saved_chunks, k=15, use_dense=False)
        return None

    collection_name = re.sub(r'[^a-z0-9]+', '_', company.lower().strip())
    collection_path = os.path.join(CHROMA_PERSIST_DIR, f"ars_{collection_name}_{year}")

    if not os.path.exists(collection_path) or not os.listdir(collection_path):
        return None   # Report has never been ingested

    embed_model = get_embedding_model()
    vectorstore, _ = load_or_create_vectorstore(company, year, embedding_model=embed_model)

    if saved_chunks:
        return build_ensemble_retriever(vectorstore, saved_chunks, k=15, use_dense=True)

    # Fallback: dense-only if chunks weren't saved
    return vectorstore.as_retriever(search_kwargs={"k": 15})


def _make_session_key(company: str, year: str) -> str:
    """Mirrors the session key logic in core/chat.py."""
    return f"{re.sub(r'[^a-z0-9]', '_', company.lower())}_{year}"