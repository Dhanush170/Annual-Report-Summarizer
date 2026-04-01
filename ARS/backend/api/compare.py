"""
api/compare.py
POST /compare — generates a cross-year delta report between Year A and Year B.
Both years must already have summaries saved (run pipeline for each first).
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth.deps import get_current_user
from core.comparator import generate_cross_year_delta_report

router = APIRouter()


class CompareRequest(BaseModel):
    company: str
    year_a:  str   # baseline (earlier year)
    year_b:  str   # comparison (later year)


@router.post("/")
def compare(
    req: CompareRequest,
    user: dict = Depends(get_current_user),
):
    """
    Generates a section-by-section delta report + executive summary.

    Request body:
        {company, year_a, year_b}

    Response shape:
        {
            "company": "TCS",
            "year_a":  "2023",
            "year_b":  "2024",
            "deltas": {
                "business_information": "**What Improved:** ...",
                "financial_statements": "...",
                ...
                "executive_delta": "Overall, TCS showed..."
            }
        }
    """
    try:
        deltas = generate_cross_year_delta_report(
            company=req.company,
            year_a=req.year_a,
            year_b=req.year_b,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "company": req.company,
        "year_a":  req.year_a,
        "year_b":  req.year_b,
        "deltas":  deltas,
    }