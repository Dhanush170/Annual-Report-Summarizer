"""
api/summaries.py
GET /summaries/{company}/{year} — returns all 8 section summaries for a report.
Used by the ReportView page to render section cards.
"""
from fastapi import APIRouter, Depends, HTTPException
from auth.deps import get_current_user
from core.chat import start_chat_session
from core.pipeline import get_or_rebuild_retriever
from core.summarizer import load_summaries, save_summaries, summarize_all_sections
from core.prompts import ANNUAL_REPORT_SECTIONS

router = APIRouter()


@router.get("/{company}/{year}")
def get_summaries(
    company: str,
    year: str,
    user: dict = Depends(get_current_user),
):
    """
    Returns the cached summaries for a given company + year.

    Response shape:
        {
            "company":      "TCS",
            "year":         "2024",
            "generated_at": "2025-01-15 10:30:00",
            "summaries": {
                "business_information": {
                    "label": "Business Information",
                    "text":  "..."
                },
                ...
            }
        }
    """
    data = load_summaries(company, year)

    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No summaries found for '{company} {year}'. Run the pipeline first."
        )

    # Enrich each summary with its display label from prompts.py
    enriched = {}
    for key, text in data["summaries"].items():
        enriched[key] = {
            "label": ANNUAL_REPORT_SECTIONS.get(key, {}).get("label", key),
            "text":  text,
        }

    return {
        "company":      data["company"],
        "year":         data["year"],
        "generated_at": data["generated_at"],
        "summaries":    enriched,
    }


@router.post("/{company}/{year}/resummarize")
def resummarize_report(
    company: str,
    year: str,
    user: dict = Depends(get_current_user),
):
    """
    Re-generates section summaries from cached retrieval data.

    This endpoint does not require re-uploading the PDF. It rebuilds the
    retriever from persisted report artifacts (chunks/vector cache), runs
    summarization, stores the refreshed summaries, and returns the same shape
    as GET /summaries/{company}/{year}.
    """
    retriever = get_or_rebuild_retriever(company, year)
    if not retriever:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No cached retrieval data found for '{company} {year}'. "
                "Please upload the report and run the pipeline first."
            ),
        )

    summaries = summarize_all_sections(retriever)
    save_summaries(summaries, company, year)
    start_chat_session(company, year, retriever)

    refreshed = load_summaries(company, year)
    if not refreshed:
        raise HTTPException(status_code=500, detail="Failed to save refreshed summaries.")

    enriched = {}
    for key, text in refreshed["summaries"].items():
        enriched[key] = {
            "label": ANNUAL_REPORT_SECTIONS.get(key, {}).get("label", key),
            "text": text,
        }

    return {
        "company": refreshed["company"],
        "year": refreshed["year"],
        "generated_at": refreshed["generated_at"],
        "summaries": enriched,
    }