"""
core/retriever.py
Ports Notebook Module 6.
Custom HybridEnsembleRetriever — version-stable, no fragile LangChain imports.
BM25 (0.4 weight) + Dense MMR (0.6 weight) merged via Reciprocal Rank Fusion.
"""
from langchain_community.retrievers import BM25Retriever
from langchain_chroma import Chroma
from typing import Optional


class HybridEnsembleRetriever:
    """
    Combines BM25 keyword search with dense semantic search.
    Merges results using Reciprocal Rank Fusion (RRF, k=60).

    - BM25  → keyword precision  (exact term matches)
    - Dense → semantic recall    (meaning-based matches)
    - RRF   → stable rank merging without score normalization issues

    Exposes .invoke(query) — drop-in compatible with LangChain retrievers.
    """

    def __init__(self, bm25_retriever, dense_retriever, weights=(0.4, 0.6), k: int = 8):
        self.bm25    = bm25_retriever
        self.dense   = dense_retriever
        self.weights = weights
        self.k       = k

    def invoke(self, query: str) -> list:
        """Retrieve from both sources and merge by RRF score."""
        bm25_docs  = self.bm25.invoke(query)
        dense_docs = self.dense.invoke(query)

        RRF_K = 60   # Standard RRF constant — higher = smoother rank influence
        scores: dict       = {}
        seen_content: dict = {}

        for rank, doc in enumerate(bm25_docs):
            key = doc.page_content[:120]
            if key not in scores:
                scores[key] = 0.0
                seen_content[key] = doc
            scores[key] += self.weights[0] * (1.0 / (RRF_K + rank + 1))

        for rank, doc in enumerate(dense_docs):
            key = doc.page_content[:120]
            if key not in scores:
                scores[key] = 0.0
                seen_content[key] = doc
            scores[key] += self.weights[1] * (1.0 / (RRF_K + rank + 1))

        # Sort by fused score descending, return top-k
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [seen_content[key] for key, _ in ranked[:self.k]]

    def get_relevant_documents(self, query: str) -> list:
        """Legacy LangChain interface alias."""
        return self.invoke(query)


class BM25OnlyRetriever:
    """Stable fallback retriever that uses keyword retrieval only."""

    def __init__(self, bm25_retriever):
        self.bm25 = bm25_retriever

    def invoke(self, query: str) -> list:
        return self.bm25.invoke(query)

    def get_relevant_documents(self, query: str) -> list:
        return self.invoke(query)


def build_ensemble_retriever(
    vectorstore: Optional[Chroma],
    chunks: list,
    k: int = 12,
    use_dense: bool = True,
):
    """
    Constructs a HybridEnsembleRetriever from a vectorstore and chunk list.

    Args:
        vectorstore: Loaded Chroma vectorstore
        chunks:      Document chunks — needed to build the BM25 in-memory index
        k:           Number of results to return per query

    Returns:
        HybridEnsembleRetriever or BM25OnlyRetriever ready to call with .invoke(query)
    """
    # BM25 — pure keyword matching, no API calls, instantaneous
    bm25_retriever   = BM25Retriever.from_documents(chunks)
    bm25_retriever.k = k

    if not use_dense or vectorstore is None:
        return BM25OnlyRetriever(bm25_retriever)

    # Dense MMR — reduces redundant chunks in results
    dense_retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": k * 2}
    )

    return HybridEnsembleRetriever(
        bm25_retriever=bm25_retriever,
        dense_retriever=dense_retriever,
        weights=(0.4, 0.6),
        k=k
    )