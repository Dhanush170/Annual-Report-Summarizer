"""
core/chat.py
Ports Notebook Module 12.
Per-report chat sessions with rolling conversation history.
History is persisted to disk as JSON so sessions survive server restarts.
Also contains save_chunks/load_chunks used by the pipeline orchestrator.
"""
import os
import re
import json
import time
from typing import Dict, List, Optional

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document

from core.config import GROQ_API_KEY, GROQ_MODEL, CHAT_HISTORY_DIR, CHUNKS_DIR


# ─────────────────────────────────────────────
# Chunk persistence (used by pipeline.py)
# ─────────────────────────────────────────────

def save_chunks(chunks: list, company: str, year: str):
    """
    Saves document chunks to disk as JSON.
    Required so BM25 can be rebuilt from cache on subsequent server starts —
    without this, cached loads fall back to dense-only retrieval.
    """
    filename = f"{re.sub(r'[^a-z0-9_]', '_', company.lower())}_{year}_chunks.json"
    path = os.path.join(CHUNKS_DIR, filename)
    payload = [
        {"page_content": c.page_content, "metadata": c.metadata}
        for c in chunks
    ]
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False)


def load_chunks(company: str, year: str) -> Optional[list]:
    """
    Loads saved chunks from disk.
    Returns a list of Document objects, or None if not found.
    """
    filename = f"{re.sub(r'[^a-z0-9_]', '_', company.lower())}_{year}_chunks.json"
    path = os.path.join(CHUNKS_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    return [Document(page_content=r["page_content"], metadata=r["metadata"]) for r in raw]


# ─────────────────────────────────────────────
# Chat session state (in-memory, per server process)
# ─────────────────────────────────────────────

# Active sessions live here. Key: session_key string
_ACTIVE_SESSIONS: Dict[str, Dict] = {}


def _get_session_key(company: str, year: str) -> str:
    """Creates a consistent session key from company + year."""
    return f"{re.sub(r'[^a-z0-9]', '_', company.lower())}_{year}"


def _load_chat_history(session_key: str) -> List[Dict]:
    """Loads persisted chat history from disk (survives server restarts)."""
    path = os.path.join(CHAT_HISTORY_DIR, f"{session_key}.json")
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return []


def _save_chat_history(session_key: str, history: List[Dict]):
    """Persists chat history to disk after every message."""
    path = os.path.join(CHAT_HISTORY_DIR, f"{session_key}.json")
    with open(path, 'w') as f:
        json.dump(history, f, indent=2)


# ─────────────────────────────────────────────
# Session management
# ─────────────────────────────────────────────

def start_chat_session(company: str, year: str, retriever) -> str:
    """
    Initializes or resumes a chat session for a company+year report.
    Loads prior conversation history from disk if it exists.

    Returns:
        session_key string (use this in all subsequent chat() calls)
    """
    session_key = _get_session_key(company, year)

    if session_key not in _ACTIVE_SESSIONS:
        history = _load_chat_history(session_key)
        _ACTIVE_SESSIONS[session_key] = {
            "retriever": retriever,
            "history":   history,
            "company":   company,
            "year":      year,
        }

    return session_key


def chat(session_key: str, user_message: str, k_history: int = 5) -> str:
    """
    Sends a message in an active chat session and returns the LLM's answer.

    Args:
        session_key:   From start_chat_session()
        user_message:  The user's question
        k_history:     How many recent turns to include as conversation context (default: 5)

    Returns:
        Assistant's response string

    Raises:
        ValueError: if session is not initialized
    """
    if session_key not in _ACTIVE_SESSIONS:
        raise ValueError(
            f"Session '{session_key}' not found. Call start_chat_session() first."
        )

    session   = _ACTIVE_SESSIONS[session_key]
    retriever = session["retriever"]
    history   = session["history"]
    company   = session["company"]
    year      = session["year"]

    # Step 1: Retrieve relevant document context
    docs = retriever.invoke(user_message)
    context = "\n\n".join(
        f"[Page {d.metadata.get('page_number', '?')}] {d.page_content}"
        for d in docs
    )

    # Step 2: Build rolling history string (last k_history turns only)
    recent = history[-k_history:] if len(history) > k_history else history
    history_str = "\n".join(
        f"{turn['role'].upper()}: {turn['content']}"
        for turn in recent
    )

    system = (
        f"You are an expert financial analyst for {company}'s {year} Annual Report.\n"
        f"Answer questions based ONLY on the retrieved context below.\n"
        f"Be precise, factual, and cite page numbers when available.\n"
        f"If the answer is not in the context, say so clearly — do not fabricate."
    )

    user_prompt = (
        f"## Conversation History:\n"
        f"{history_str if history_str else '(No prior conversation)'}\n\n"
        f"## Retrieved Context from {year} Annual Report:\n{context}\n\n"
        f"## User Question:\n{user_message}"
    )

    llm = ChatGroq(
        temperature=0.2,
        groq_api_key=GROQ_API_KEY,
        model_name=GROQ_MODEL
    )

    answer = ""
    for attempt in range(3):
        try:
            response = llm.invoke([
                SystemMessage(content=system),
                HumanMessage(content=user_prompt)
            ])
            answer = response.content
            break
        except Exception as e:
            if "rate_limit_exceeded" in str(e) or "429" in str(e):
                wait = 15 * (attempt + 1)
                time.sleep(wait)
            else:
                raise e

    # Step 3: Persist updated history
    history.append({"role": "user",      "content": user_message})
    history.append({"role": "assistant", "content": answer})
    _save_chat_history(session_key, history)

    return answer


def clear_chat_history(session_key: str):
    """Clears history for a session — both in memory and on disk."""
    if session_key in _ACTIVE_SESSIONS:
        _ACTIVE_SESSIONS[session_key]["history"] = []
    _save_chat_history(session_key, [])