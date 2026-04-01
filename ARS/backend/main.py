import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv()

from auth.google_oauth import router as auth_router
from api import reports, pipeline, summaries, translate, audio, compare, chat

app = FastAPI(
    title="ARS — Annual Report Summarizer API",
    version="1.0.0",
    description="Backend API for the Annual Report Summarizer project."
)

# ── CORS — allow React dev server to call this API ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Serve generated audio files as static assets ──
AUDIO_DIR = Path(__file__).parent / "data" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/audio-files", StaticFiles(directory=str(AUDIO_DIR)), name="audio")

# ── Register all route groups ──
app.include_router(auth_router,       prefix="/auth",      tags=["Authentication"])
app.include_router(reports.router,    prefix="/reports",   tags=["Reports"])
app.include_router(pipeline.router,   prefix="/pipeline",  tags=["Pipeline"])
app.include_router(summaries.router,  prefix="/summaries", tags=["Summaries"])
app.include_router(translate.router,  prefix="/translate", tags=["Translation"])
app.include_router(audio.router,      prefix="/audio",     tags=["Audio"])
app.include_router(compare.router,    prefix="/compare",   tags=["Comparison"])
app.include_router(chat.router,       prefix="/chat",      tags=["Chat"])


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ARS API is running",
        "docs":   "/docs",
        "redoc":  "/redoc"
    }