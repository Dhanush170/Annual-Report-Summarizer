"""
core/summarizer.py
Ports Notebook Module 8.
Parallel section summarization using Groq (llama-3.3-70b-versatile).
max_workers=4 + 1.5s stagger keeps under Groq free-tier 12,000 TPM limit.
Retry logic handles transient 429 rate-limit errors.
"""
import os
import re
import json
import time
from typing import Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from core.config import GROQ_API_KEY, GROQ_MODEL, SUMMARIES_DIR
from core.prompts import ANNUAL_REPORT_SECTIONS
from core.retriever import HybridEnsembleRetriever


# ─────────────────────────────────────────────
# System prompt — governs all section summaries
# ─────────────────────────────────────────────

SUMMARIZATION_SYSTEM_PROMPT = """You are an expert financial analyst specializing in corporate annual report analysis.
STRICT RULES:
- The summary must be from 80 to 100 words
- NEVER say a section is "absent", "not found", or "not mentioned" — always work with whatever context is provided
- If direct content is limited, infer from surrounding context and clearly note it
- Be precise and data-driven — cite specific figures, names, and dates when available
- Be concise but substantive — every sentence must add value
- No filler phrases like "the company aims to" or "management noted efforts to"
- Always end with a clearly labeled 'Insight:' line that adds genuine analytical value"""


# ─────────────────────────────────────────────
# Single-section worker (runs in thread pool)
# ─────────────────────────────────────────────

def _summarize_single_section(
    section_key: str,
    section_config: Dict,
    retriever: HybridEnsembleRetriever,
    llm: ChatGroq
) -> Tuple[str, str]:
    """
    Retrieves context for one section and generates its summary.
    Returns: (section_key, summary_text)
    Retries up to 3 times on Groq rate-limit errors (429).
    """
    retrieval_prompt = section_config["retrieval_prompt"]
    summary_prompt   = section_config["summary_prompt"]
    label            = section_config["label"]

    # Retrieve relevant chunks from the vectorstore
    docs = retriever.invoke(retrieval_prompt)
    context = "\n\n".join(
        f"[Page {doc.metadata.get('page_number', '?')}]\n{doc.page_content}"
        for doc in docs
    )

    user_message = (
        f"## Section: {label}\n\n"
        f"### Retrieved Context from Annual Report:\n{context}\n\n"
        f"### Your Task:\n{summary_prompt}"
    )

    messages = [
        SystemMessage(content=SUMMARIZATION_SYSTEM_PROMPT),
        HumanMessage(content=user_message)
    ]

    for attempt in range(3):
        try:
            response = llm.invoke(messages)
            return section_key, response.content
        except Exception as e:
            if "rate_limit_exceeded" in str(e) or "429" in str(e):
                wait = 15 * (attempt + 1)   # 15s → 30s → 45s
                time.sleep(wait)
            else:
                raise e

    return section_key, f"[Failed after 3 retries — rate limit on '{label}']"


# ─────────────────────────────────────────────
# Main: parallel summarization
# ─────────────────────────────────────────────

def summarize_all_sections(
    retriever: HybridEnsembleRetriever,
    sections: Dict = None,
    max_workers: int = 4
) -> Dict[str, str]:
    """
    Summarizes all 8 sections with staggered parallel execution.
    Submissions are spaced 1.5s apart to stay under Groq's 12,000 TPM cap.

    Args:
        retriever:   HybridEnsembleRetriever for this report
        sections:    Section config dict (defaults to ANNUAL_REPORT_SECTIONS)
        max_workers: Max concurrent threads (default: 4)

    Returns:
        {section_key: summary_text}
    """
    if sections is None:
        sections = ANNUAL_REPORT_SECTIONS

    llm = ChatGroq(
        temperature=0.3,
        groq_api_key=GROQ_API_KEY,
        model_name=GROQ_MODEL
    )

    summaries: Dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for key, cfg in sections.items():
            future = executor.submit(_summarize_single_section, key, cfg, retriever, llm)
            futures[future] = key
            time.sleep(1.5)   # stagger submissions to spread token load

        for future in as_completed(futures):
            section_key = futures[future]
            try:
                key, summary = future.result()
                summaries[key] = summary
            except Exception as e:
                summaries[section_key] = f"[Error generating summary: {e}]"

    return summaries


# ─────────────────────────────────────────────
# Persistence helpers
# ─────────────────────────────────────────────

def save_summaries(summaries: Dict, company: str, year: str) -> str:
    """Saves summaries dict to a JSON file on disk."""
    filename = f"{re.sub(r'[^a-z0-9_]', '_', company.lower())}_{year}.json"
    path = os.path.join(SUMMARIES_DIR, filename)
    payload = {
        "company":      company,
        "year":         year,
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "summaries":    summaries
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return path


def load_summaries(company: str, year: str) -> Optional[Dict]:
    """Loads cached summaries from disk. Returns None if not found."""
    filename = f"{re.sub(r'[^a-z0-9_]', '_', company.lower())}_{year}.json"
    path = os.path.join(SUMMARIES_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None