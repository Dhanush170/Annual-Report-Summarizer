"""
core/comparator.py
Ports Notebook Module 11.
Cross-year comparison — generates a structured delta report between Year A and Year B.
Same stagger + retry pattern as summarizer.py to respect Groq TPM limits.
"""
import time
from typing import Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from core.config import GROQ_API_KEY, GROQ_MODEL
from core.prompts import ANNUAL_REPORT_SECTIONS
from core.summarizer import load_summaries


COMPARISON_SYSTEM_PROMPT = """You are a senior financial analyst with deep expertise in comparative annual report analysis.
When comparing two years of reports for the same company:
- Be specific: quote or reference numbers/facts from each year
- Be analytical: identify trends, reversals, and trajectory changes
- Be candid: highlight both positive improvements and concerning shifts
- Format output clearly with the specified structure"""


def generate_section_delta(
    section_key: str,
    summary_year_a: str,
    summary_year_b: str,
    year_a: str,
    year_b: str,
    llm: ChatGroq
) -> str:
    """
    Generates a structured comparison for one section between two years.
    Retries up to 3 times on rate-limit errors.
    """
    label = ANNUAL_REPORT_SECTIONS[section_key]["label"]

    prompt = (
        f"Compare the '{label}' section between the {year_a} and {year_b} annual reports.\n\n"
        f"## {year_a} Summary:\n{summary_year_a}\n\n"
        f"## {year_b} Summary:\n{summary_year_b}\n\n"
        f"Provide your comparison in this exact format:\n"
        f"**What Improved:** [specific improvements from {year_a} to {year_b}]\n"
        f"**What Declined:** [specific declines or regressions]\n"
        f"**New Developments:** [things that appear in {year_b} but not {year_a}]\n"
        f"**Dropped/De-emphasized:** [things prominent in {year_a} but absent in {year_b}]\n"
        f"**Trend Signal:** [one-line overall trajectory assessment]\n\n"
        f"Be concise, specific, and data-driven. (~100 words total)"
    )

    messages = [
        SystemMessage(content=COMPARISON_SYSTEM_PROMPT),
        HumanMessage(content=prompt)
    ]

    for attempt in range(3):
        try:
            response = llm.invoke(messages)
            return response.content
        except Exception as e:
            if "rate_limit_exceeded" in str(e) or "429" in str(e):
                wait = 15 * (attempt + 1)
                time.sleep(wait)
            else:
                raise e

    return f"[Failed after 3 retries — rate limit on '{label}']"


def generate_cross_year_delta_report(
    company: str,
    year_a: str,
    year_b: str
) -> Dict[str, str]:
    """
    Generates a full delta report comparing year_a vs year_b for a company.
    Both years must already have summaries saved on disk.

    Args:
        company: Company name (must match saved summaries exactly)
        year_a:  Baseline year (earlier)
        year_b:  Comparison year (later)

    Returns:
        {section_key: delta_text, "executive_delta": executive_summary_text}

    Raises:
        ValueError: if years are same, or summaries not found
    """
    if year_a == year_b:
        raise ValueError(
            f"year_a and year_b cannot be the same ({year_a}). Choose two different years."
        )

    data_a = load_summaries(company, year_a)
    data_b = load_summaries(company, year_b)

    if not data_a:
        raise ValueError(f"No saved summaries for {company} {year_a}. Run the pipeline first.")
    if not data_b:
        raise ValueError(f"No saved summaries for {company} {year_b}. Run the pipeline first.")

    summaries_a = data_a["summaries"]
    summaries_b = data_b["summaries"]

    llm = ChatGroq(
        temperature=0.3,
        groq_api_key=GROQ_API_KEY,
        model_name=GROQ_MODEL
    )

    deltas: Dict[str, str] = {}

    # Staggered parallel execution — same pattern as summarizer.py
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {}
        for key in ANNUAL_REPORT_SECTIONS:
            future = executor.submit(
                generate_section_delta,
                key,
                summaries_a.get(key, "Not available"),
                summaries_b.get(key, "Not available"),
                year_a, year_b, llm
            )
            futures[future] = key
            time.sleep(1.5)

        for future in as_completed(futures):
            key = futures[future]
            try:
                deltas[key] = future.result()
            except Exception as e:
                deltas[key] = f"[Comparison error: {e}]"

    # Generate executive-level overall delta
    section_context = "\n".join(
        f"{k}: {v[:200]}..." for k, v in deltas.items()
    )
    executive_prompt = (
        f"Based on all section comparisons between {year_a} and {year_b} for {company}, "
        f"write a 4-5 sentence executive-level delta summary covering:\n"
        f"1. Overall business trajectory\n"
        f"2. Most significant financial shift\n"
        f"3. Most important strategic change\n"
        f"4. Biggest new risk or opportunity\n"
        f"Be direct and analytically sharp.\n\n"
        f"Section deltas for context:\n{section_context}"
    )

    exec_response = llm.invoke([
        SystemMessage(content=COMPARISON_SYSTEM_PROMPT),
        HumanMessage(content=executive_prompt)
    ])
    deltas["executive_delta"] = exec_response.content

    return deltas