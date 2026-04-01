"""
core/translation.py
Ports Notebook Module 9.
Translates section summaries using deep-translator (Google Translate backend).
No API key required. Handles texts > 5000 chars by splitting into sentence chunks.
"""
from typing import Dict
from deep_translator import GoogleTranslator


# ── Supported language map: display name → ISO code ──
SUPPORTED_LANGUAGES = {
    "English":            "en",
    "Hindi":              "hi",
    "Tamil":              "ta",
    "French":             "fr",
    "Spanish":            "es",
    "German":             "de",
    "Arabic":             "ar",
    "Chinese (Simplified)": "zh-CN",
    "Japanese":           "ja",
    "Portuguese":         "pt",
}


def translate_text(text: str, target_language_code: str, source: str = "en") -> str:
    """
    Translates a single text string to the target language.
    Handles texts longer than deep-translator's 5000-char limit
    by splitting on sentence boundaries and translating each chunk.

    Args:
        text:                  Text to translate
        target_language_code:  ISO code (e.g., 'hi', 'ta', 'fr')
        source:                Source language (default: 'en')

    Returns:
        Translated text string
    """
    if target_language_code == source:
        return text   # No translation needed

    MAX_CHARS = 4500  # stay under deep-translator's 5000-char hard limit
    translator = GoogleTranslator(source=source, target=target_language_code)

    if len(text) <= MAX_CHARS:
        return translator.translate(text)

    # Split into sentence-level chunks for long texts
    translated_parts = []
    sentences = text.split('. ')
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) < MAX_CHARS:
            current += sentence + ". "
        else:
            if current:
                translated_parts.append(translator.translate(current.strip()))
            current = sentence + ". "

    if current:
        translated_parts.append(translator.translate(current.strip()))

    return " ".join(translated_parts)


def translate_summaries(
    summaries: Dict[str, str],
    target_language_code: str
) -> Dict[str, str]:
    """
    Translates all section summaries to the target language.

    Args:
        summaries:             {section_key: summary_text}
        target_language_code:  ISO code (e.g., 'hi')

    Returns:
        New dict with translated values. Original dict is not modified.
    """
    if target_language_code == "en":
        return summaries   # already English

    translated: Dict[str, str] = {}

    for key, text in summaries.items():
        try:
            translated[key] = translate_text(text, target_language_code)
        except Exception as e:
            translated[key] = f"[Translation error: {e}]"

    return translated