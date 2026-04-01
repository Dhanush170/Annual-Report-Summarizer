"""
core/config.py
Central configuration — loaded once at startup.
All other core modules import from here instead of reading .env themselves.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── API Keys ──
GROQ_API_KEY    = os.getenv("GROQ_API_KEY")
HF_API_KEY      = os.getenv("HF_API_KEY")

# ── Model names ──
GROQ_MODEL      = "llama-3.3-70b-versatile"
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"

# ── Data directories (all local, under backend/data/) ──
BASE_DATA_DIR      = Path(__file__).parent.parent / "data"
CHROMA_PERSIST_DIR = str(BASE_DATA_DIR / "chroma_store")
CHAT_HISTORY_DIR   = str(BASE_DATA_DIR / "chat_history")
SUMMARIES_DIR      = str(BASE_DATA_DIR / "summaries")
CHUNKS_DIR         = str(BASE_DATA_DIR / "chunks")
AUDIO_OUTPUT_DIR   = str(BASE_DATA_DIR / "audio")
UPLOADS_DIR        = str(BASE_DATA_DIR / "uploads")

# ── Ensure all directories exist on startup ──
for _dir in [
    CHROMA_PERSIST_DIR,
    CHAT_HISTORY_DIR,
    SUMMARIES_DIR,
    CHUNKS_DIR,
    AUDIO_OUTPUT_DIR,
    UPLOADS_DIR,
]:
    Path(_dir).mkdir(parents=True, exist_ok=True)