"""
api/chat.py
POST /chat/message — sends a question about a report and gets an answer
POST /chat/clear   — clears conversation history for a report session

The chat session is auto-initialized on first message if not already active —
no need for the frontend to call a separate "init session" endpoint.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth.deps import get_current_user
from core.chat import (
    chat,
    start_chat_session,
    clear_chat_history,
    _get_session_key,
    _ACTIVE_SESSIONS,
)
from core.pipeline import get_or_rebuild_retriever

router = APIRouter()


class ChatRequest(BaseModel):
    company: str
    year:    str
    message: str


class ClearRequest(BaseModel):
    company: str
    year:    str


@router.post("/message")
def send_message(
    req: ChatRequest,
    user: dict = Depends(get_current_user),
):
    """
    Sends a question about a report and returns the LLM's answer.

    Request body:
        {company, year, message}

    Response shape:
        {
            "answer":      "Revenue grew 8% YoY to ₹2.4 lakh crore...",
            "session_key": "tcs_2024"
        }

    Auto-initializes the session on first message if it doesn't exist yet.
    """
    session_key = _get_session_key(req.company, req.year)

    # Auto-initialize session if not yet active
    if session_key not in _ACTIVE_SESSIONS:
        retriever = get_or_rebuild_retriever(req.company, req.year)
        if retriever is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Report '{req.company} {req.year}' not found. "
                    "Run the pipeline first to ingest this report."
                )
            )
        start_chat_session(req.company, req.year, retriever)

    answer = chat(session_key, req.message)

    return {"answer": answer, "session_key": session_key}


@router.post("/clear")
def clear_session(
    req: ClearRequest,
    user: dict = Depends(get_current_user),
):
    """
    Clears conversation history for a report session.
    """
    session_key = _get_session_key(req.company, req.year)
    clear_chat_history(session_key)
    return {"status": "cleared", "session_key": session_key}