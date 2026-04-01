"""
api/reports.py
GET /reports — returns all company+year reports stored on disk.
Used by the Dashboard page to render company cards.
"""
import os
import re
import glob
import shutil

from fastapi import APIRouter, Depends
from auth.deps import get_current_user
from core.vectorstore import list_stored_reports
from core.config import (
    SUMMARIES_DIR,
    CHROMA_PERSIST_DIR,
    CHUNKS_DIR,
    CHAT_HISTORY_DIR,
    AUDIO_OUTPUT_DIR,
)
from core.chat import _get_session_key, _ACTIVE_SESSIONS

router = APIRouter()


@router.get("/")
def get_all_reports(user: dict = Depends(get_current_user)):
    """
    Returns a dict of all ingested reports grouped by company.

    Response shape:
        {
            "TCS":     ["2022", "2023", "2024"],
            "Infosys": ["2023"]
        }
    """
    return list_stored_reports()


@router.delete("/{company}/{year}")
def delete_report_artifacts(
    company: str,
    year: str,
    user: dict = Depends(get_current_user),
):
    """
    Permanently deletes all artifacts for a company-year report.

    Artifacts removed:
      - summaries JSON
      - vectorstore collection directory
      - saved chunks JSON
      - chat history JSON + in-memory session
      - generated audio files for that company-year
    """
    slug_summary = re.sub(r'[^a-z0-9_]', '_', company.lower())
    slug_vector = re.sub(r'[^a-z0-9]+', '_', company.lower().strip())
    session_key = _get_session_key(company, year)

    removed = {
        "summaries": False,
        "vectorstore": False,
        "chunks": False,
        "chat_history": False,
        "audio_files": 0,
    }

    summary_path = os.path.join(SUMMARIES_DIR, f"{slug_summary}_{year}.json")
    if os.path.exists(summary_path):
        os.remove(summary_path)
        removed["summaries"] = True

    vector_dir = os.path.join(CHROMA_PERSIST_DIR, f"ars_{slug_vector}_{year}")
    if os.path.isdir(vector_dir):
        shutil.rmtree(vector_dir, ignore_errors=True)
        removed["vectorstore"] = True

    chunks_path = os.path.join(CHUNKS_DIR, f"{slug_summary}_{year}_chunks.json")
    if os.path.exists(chunks_path):
        os.remove(chunks_path)
        removed["chunks"] = True

    chat_path = os.path.join(CHAT_HISTORY_DIR, f"{session_key}.json")
    if os.path.exists(chat_path):
        os.remove(chat_path)
        removed["chat_history"] = True

    if session_key in _ACTIVE_SESSIONS:
        _ACTIVE_SESSIONS.pop(session_key, None)

    audio_pattern = os.path.join(AUDIO_OUTPUT_DIR, f"{slug_summary}_{year}_*.mp3")
    audio_files = glob.glob(audio_pattern)
    for audio_file in audio_files:
        try:
            os.remove(audio_file)
        except OSError:
            continue
    removed["audio_files"] = len(audio_files)

    deleted_any = (
        removed["summaries"]
        or removed["vectorstore"]
        or removed["chunks"]
        or removed["chat_history"]
        or removed["audio_files"] > 0
    )

    return {
        "status": "deleted" if deleted_any else "not_found",
        "company": company,
        "year": year,
        "removed": removed,
    }