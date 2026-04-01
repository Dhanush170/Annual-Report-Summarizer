"""
core/vectorstore.py
Ports Notebook Module 5.
Manages the ChromaDB persistent vector store — one collection per company+year.
On first run → embeds all chunks via HF API, saves to disk.
On repeat run → loads from disk instantly (no re-embedding).
"""
import os
import re
import json
from typing import List, Dict, Optional, Tuple

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEndpointEmbeddings

from core.config import HF_API_KEY, EMBEDDING_MODEL, CHROMA_PERSIST_DIR, SUMMARIES_DIR


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _make_collection_name(company: str, year: str) -> str:
    """
    Creates a safe, consistent ChromaDB collection name.
    e.g., 'Apple Inc' + '2023' → 'ars_apple_inc_2023'
    """
    slug = re.sub(r'[^a-z0-9]+', '_', company.lower().strip())
    return f"ars_{slug}_{year}"


def get_embedding_model() -> HuggingFaceEndpointEmbeddings:
    """
    Initializes the HuggingFace Inference API embedding model.
    Embeddings run on HF GPU servers — zero local compute required.
    """
    return HuggingFaceEndpointEmbeddings(
        model=EMBEDDING_MODEL,
        huggingfacehub_api_token=HF_API_KEY
    )


# ─────────────────────────────────────────────
# Core: load or create vector store
# ─────────────────────────────────────────────

def load_or_create_vectorstore(
    company: str,
    year: str,
    chunks: Optional[List[Document]] = None,
    embedding_model=None,
    force_recreate: bool = False,
) -> Tuple[Chroma, bool]:
    """
    Loads an existing ChromaDB collection from disk if it exists,
    otherwise embeds all chunks and creates a new one.

    Args:
        company:         Company name (e.g., 'TCS')
        year:            Report year (e.g., '2024')
        chunks:          Document chunks — required only on first run
        embedding_model: Pass an existing instance to avoid re-initializing

    Returns:
        (vectorstore, was_cached)
        was_cached=True → loaded from disk instantly
        was_cached=False → freshly embedded and saved
    """
    collection_name = _make_collection_name(company, year)
    collection_path = os.path.join(CHROMA_PERSIST_DIR, collection_name)

    if embedding_model is None:
        embedding_model = get_embedding_model()

    # ── Cache HIT: collection folder exists and is non-empty ──
    if not force_recreate and os.path.exists(collection_path) and os.listdir(collection_path):
        client = chromadb.PersistentClient(path=collection_path)
        vectorstore = Chroma(
            client=client,
            collection_name=collection_name,
            embedding_function=embedding_model
        )
        return vectorstore, True

    # ── Cache MISS: embed and persist ──
    if not chunks:
        raise ValueError(
            "chunks must be provided when creating a new vector store collection."
        )

    os.makedirs(collection_path, exist_ok=True)
    client = chromadb.PersistentClient(path=collection_path)

    # Embed in batches of 50 to respect HF API rate limits
    BATCH_SIZE = 50
    vectorstore = None

    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        if vectorstore is None:
            vectorstore = Chroma.from_documents(
                documents=batch,
                embedding=embedding_model,
                collection_name=collection_name,
                client=client
            )
        else:
            vectorstore.add_documents(batch)

    return vectorstore, False


# ─────────────────────────────────────────────
# Utility: list all stored reports
# ─────────────────────────────────────────────

def list_stored_reports() -> Dict[str, List[str]]:
    """
    Reads saved summaries JSON files to get the EXACT original company names
    and all available years. This preserves the company name as the user typed it
    (e.g. 'TCS' stays 'TCS', not 'Tcs').

    Falls back to scanning ChromaDB directory if no summaries exist yet.

    Returns: { "TCS": ["2022", "2023", "2024"], "Infosys": ["2023"] }
    """
    reports: Dict[str, List[str]] = {}

    # ── Primary: read from summaries JSON files (exact original names) ──
    if os.path.exists(SUMMARIES_DIR):
        for filename in os.listdir(SUMMARIES_DIR):
            if not filename.endswith('.json'):
                continue
            filepath = os.path.join(SUMMARIES_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                company = data.get('company', '').strip()
                year    = data.get('year', '').strip()
                if company and year:
                    reports.setdefault(company, []).append(year)
            except Exception:
                continue

    # ── Fallback: scan ChromaDB dir if summaries is empty ──
    if not reports and os.path.exists(CHROMA_PERSIST_DIR):
        for entry in os.listdir(CHROMA_PERSIST_DIR):
            match = re.match(r'^ars_(.+)_(\d{4})$', entry)
            if match:
                company = match.group(1).replace('_', ' ').upper()
                year    = match.group(2)
                reports.setdefault(company, []).append(year)

    for company in reports:
        reports[company].sort()

    return reports