"""
api/audio.py
POST /audio/generate — generates an MP3 for a section or full report.

Audio files are served as static files via /audio-files/ (mounted in main.py).
The endpoint returns a URL the frontend can play directly in an <audio> element.
"""
import os

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth.deps import get_current_user
from core.audio import generate_audio, generate_full_audio_summary
from core.summarizer import load_summaries

router = APIRouter()


class AudioRequest(BaseModel):
    company:       str
    year:          str
    section_key:   str   # section key OR "full_report" for the entire report
    language_code: str = "en"


@router.post("/generate")
def generate(
    req: AudioRequest,
    user: dict = Depends(get_current_user),
):
    """
    Generates and saves an MP3 file for the requested section.

    Request body:
        {company, year, section_key, language_code}
        section_key = "full_report" → generates audio for entire report

    Response shape:
        {"audio_url": "/audio-files/tcs_2024_financial_statements_en.mp3"}

    The frontend sets <audio src={audio_url}> to play it inline.
    """
    data = load_summaries(req.company, req.year)
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No summaries found for '{req.company} {req.year}'."
        )

    summaries = data["summaries"]

    if req.section_key == "full_report":
        filepath = generate_full_audio_summary(
            summaries, req.company, req.year, req.language_code
        )
    else:
        if req.section_key not in summaries:
            raise HTTPException(
                status_code=404,
                detail=f"Section '{req.section_key}' not found in summaries."
            )
        filepath = generate_audio(
            text=summaries[req.section_key],
            section_key=req.section_key,
            company=req.company,
            year=req.year,
            language_code=req.language_code,
        )

    if not filepath:
        raise HTTPException(status_code=500, detail="Audio generation failed.")

    filename  = os.path.basename(filepath)
    audio_url = f"/audio-files/{filename}"

    return {"audio_url": audio_url}