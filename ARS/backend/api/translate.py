"""
api/translate.py
POST /translate      — translates summaries for a given company+year into a target language
GET  /translate/languages — returns the supported language map for the UI dropdown
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth.deps import get_current_user
from core.summarizer import load_summaries
from core.translation import translate_summaries, SUPPORTED_LANGUAGES

router = APIRouter()


class TranslateRequest(BaseModel):
    company:              str
    year:                 str
    target_language_code: str   # e.g. "hi", "ta", "fr"


@router.get("/languages")
def get_languages():
    """
    Returns all supported language options for the translation dropdown.

    Response shape:
        {"English": "en", "Hindi": "hi", "Tamil": "ta", ...}
    """
    return SUPPORTED_LANGUAGES


@router.post("/")
def translate(
    req: TranslateRequest,
    user: dict = Depends(get_current_user),
):
    """
    Translates all 8 section summaries for a report into the target language.

    Request body:
        {company, year, target_language_code}

    Response shape:
        {
            "language": "hi",
            "translated": {
                "business_information": "...",
                ...
            }
        }
    """
    data = load_summaries(req.company, req.year)
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No summaries found for '{req.company} {req.year}'."
        )

    translated = translate_summaries(data["summaries"], req.target_language_code)

    return {
        "language":   req.target_language_code,
        "translated": translated,
    }