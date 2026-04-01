"""
api/pipeline.py
POST /pipeline/run — accepts a PDF upload and kicks off the ARS pipeline.

Because the pipeline can take 1-3 minutes for a new document,
we use FastAPI BackgroundTasks + an in-memory job store.

Flow:
  1. Frontend uploads PDF → POST /pipeline/run → gets back {job_id}
  2. Frontend polls GET /pipeline/status/{job_id} every 3 seconds
  3. When status == "done", frontend fetches summaries from GET /summaries/{company}/{year}
"""
import os
import shutil
import uuid
from typing import Dict

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile

from auth.deps import get_current_user
from core.config import UPLOADS_DIR
from core.pipeline import run_ars_pipeline

router = APIRouter()

# ── In-memory job store (resets when server restarts — fine for local/demo use) ──
_JOBS: Dict[str, Dict] = {}


# ─────────────────────────────────────────────
# Background worker
# ─────────────────────────────────────────────

def _execute_pipeline(
    job_id: str,
    pdf_path: str,
    company: str,
    year: str,
    force_reindex: bool,
    force_resummarize: bool,
):
    """Runs in a background thread. Updates job store on completion or error."""
    import traceback
    try:
        _JOBS[job_id]["status"] = "running"
        result = run_ars_pipeline(
            pdf_path=pdf_path,
            company=company,
            year=year,
            force_reindex=force_reindex,
            force_resummarize=force_resummarize,
        )
        _JOBS[job_id]["status"]     = "done"
        _JOBS[job_id]["from_cache"] = result["from_cache"]
    except Exception as e:
        _JOBS[job_id]["status"] = "error"
        _JOBS[job_id]["error"]  = str(e)
        # Print full traceback to backend terminal so you can see what went wrong
        print(f"\n[PIPELINE ERROR] job_id={job_id} company={company} year={year}")
        traceback.print_exc()


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@router.post("/run")
async def run_pipeline(
    background_tasks: BackgroundTasks,
    file: UploadFile               = File(...),
    company: str                   = Form(...),
    year: str                      = Form(...),
    force_reindex: bool            = Form(False),
    force_resummarize: bool        = Form(False),
    user: dict                     = Depends(get_current_user),
):
    """
    Accepts a PDF upload and starts the pipeline in the background.

    Form fields:
        file              — PDF file
        company           — Company name (e.g., 'TCS')
        year              — Report year (e.g., '2024')
        force_reindex     — Re-embed from scratch (default: false)
        force_resummarize — Re-summarize only (default: false)

    Returns:
        {job_id, status: "queued"}
    """
    # Save uploaded PDF to the uploads directory
    safe_name = f"{company}_{year}_{file.filename}".replace(" ", "_")
    pdf_path  = os.path.join(UPLOADS_DIR, safe_name)

    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Create a job entry and queue the background task
    job_id = str(uuid.uuid4())
    _JOBS[job_id] = {
        "status":  "queued",
        "company": company,
        "year":    year,
    }

    background_tasks.add_task(
        _execute_pipeline,
        job_id, pdf_path, company, year,
        force_reindex, force_resummarize,
    )

    return {"job_id": job_id, "status": "queued"}


@router.get("/status/{job_id}")
def get_job_status(job_id: str, user: dict = Depends(get_current_user)):
    """
    Poll this endpoint every 3 seconds after submitting a pipeline job.

    Returns:
        {status: "queued" | "running" | "done" | "error", ...}
    """
    job = _JOBS.get(job_id)
    if not job:
        return {"status": "not_found"}
    return job