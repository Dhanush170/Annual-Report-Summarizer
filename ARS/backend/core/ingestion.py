"""
core/ingestion.py
Ports Notebook Modules 3 & 4.
  - Module 3: PDF text extraction + per-page preprocessing
  - Module 4: Smart chunking with page-boundary markers
"""
import re
from typing import List, Dict

import fitz  # PyMuPDF
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ─────────────────────────────────────────────
# MODULE 3 — PDF Extraction & Preprocessing
# ─────────────────────────────────────────────

def extract_text_from_pdf(pdf_path: str) -> List[Dict]:
    """
    Opens a PDF and extracts raw text from every page.
    Returns: List of {page_number, text}
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise ValueError(f"Could not open PDF at '{pdf_path}': {e}")

    pages_data = [
        {"page_number": i + 1, "text": page.get_text()}
        for i, page in enumerate(doc)
    ]
    doc.close()
    return pages_data


def preprocess_page(text: str) -> str:
    """
    Cleans a single page's raw text:
    - Rejoins hyphenated line-breaks      (e.g., "finan-\ncial" → "financial")
    - Collapses soft newlines into spaces (preserves paragraph breaks)
    - Strips excess whitespace
    """
    text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)      # fix hyphenated words
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)        # soft newlines → space
    text = re.sub(r'[ \t]{2,}', ' ', text)              # collapse spaces/tabs
    text = re.sub(r'\n{3,}', '\n\n', text)              # max 2 consecutive newlines
    return text.strip()


def extract_and_preprocess(pdf_path: str) -> List[Dict]:
    """
    Full extraction pipeline: extract → clean all pages.
    Returns pages with both 'text' (raw) and 'cleaned_text'.
    """
    pages = extract_text_from_pdf(pdf_path)
    for page in pages:
        page["cleaned_text"] = preprocess_page(page["text"])
    return pages


# ─────────────────────────────────────────────
# MODULE 4 — Smart Chunking
# ─────────────────────────────────────────────

def chunk_document(pages: List[Dict]) -> List[Document]:
    """
    Consolidates all pages into one string with <<PAGE_N>> boundary markers,
    splits into 1000-char overlapping chunks, and attaches page_number metadata.

    Strategy:
    - Page markers are the highest-priority separator so chunks respect page boundaries
    - chunk_size=1000 / overlap=100 is optimal for dense financial text
    """
    # Build full document with page markers
    full_text = ""
    for page in pages:
        marker = f"\n\n<<PAGE_{page['page_number']}>> \n\n"
        full_text += marker + page["cleaned_text"]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
        separators=[
            r"\n\n<<PAGE_\d+>>\s\n\n",   # page boundaries (highest priority)
            "\n\n",                        # paragraph breaks
            "\n",                          # line breaks
            ". ",                          # sentence endings
            " ",                           # word boundaries (last resort)
            ""
        ],
        is_separator_regex=True
    )

    raw_chunks = splitter.create_documents([full_text])

    # Post-process: strip markers, assign page metadata
    final_chunks: List[Document] = []
    last_page = 1

    for chunk in raw_chunks:
        content = chunk.page_content

        # Track which page this chunk belongs to
        match = re.search(r"<<PAGE_(\d+)>>", content)
        if match:
            last_page = int(match.group(1))

        # Remove all <<PAGE_N>> markers from content
        cleaned = re.sub(r"<<PAGE_\d+>>\s*", "", content).strip()

        if cleaned:
            final_chunks.append(Document(
                page_content=cleaned,
                metadata={"page_number": last_page}
            ))

    return final_chunks