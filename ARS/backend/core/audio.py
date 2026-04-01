"""
core/audio.py
Ports Notebook Module 10.
Generates MP3 audio from summary text using gTTS.
IPython.display removed — audio is saved to disk and served via FastAPI static files.
"""
import os
import re
from typing import Dict

from gtts import gTTS

from core.config import AUDIO_OUTPUT_DIR
from core.prompts import ANNUAL_REPORT_SECTIONS


# ── gTTS language code mapping ──
# Some codes differ between ISO (used in translate) and gTTS
GTTS_LANG_MAP = {
    "en":    "en",
    "hi":    "hi",
    "ta":    "ta",
    "fr":    "fr",
    "es":    "es",
    "de":    "de",
    "ar":    "ar",
    "zh-CN": "zh",   # gTTS uses 'zh', not 'zh-CN'
    "ja":    "ja",
    "pt":    "pt",
}


def generate_audio(
    text: str,
    section_key: str,
    company: str,
    year: str,
    language_code: str = "en"
) -> str:
    """
    Converts text to speech and saves as an MP3 file.

    Args:
        text:          The summary text to convert
        section_key:   Section identifier (used in filename)
        company:       Company name (used in filename)
        year:          Report year (used in filename)
        language_code: ISO language code (default: 'en')

    Returns:
        Absolute path to the saved .mp3 file.
        Returns empty string if generation fails.
    """
    gtts_lang = GTTS_LANG_MAP.get(language_code, "en")
    slug = re.sub(r'[^a-z0-9_]', '_', company.lower())
    filename = f"{slug}_{year}_{section_key}_{language_code}.mp3"
    filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)

    try:
        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        tts.save(filepath)
        return filepath
    except Exception as e:
        print(f"[audio] Generation failed for '{section_key}': {e}")
        return ""


def generate_full_audio_summary(
    summaries: Dict[str, str],
    company: str,
    year: str,
    language_code: str = "en"
) -> str:
    """
    Concatenates all section summaries and generates a single full-report audio file.
    Sections are joined with a double space (natural pause in TTS).

    Returns:
        Path to saved .mp3 file.
    """
    parts = []
    for key, cfg in ANNUAL_REPORT_SECTIONS.items():
        if key in summaries:
            # Prepend section label so the listener knows which section is playing
            parts.append(f"{cfg['label']}. {summaries[key]}")

    full_text = "  ".join(parts)   # double space = natural pause in TTS

    return generate_audio(
        text=full_text,
        section_key="full_report",
        company=company,
        year=year,
        language_code=language_code
    )