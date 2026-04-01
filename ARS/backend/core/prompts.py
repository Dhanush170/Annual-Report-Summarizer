"""
core/prompts.py
Ports Notebook Module 7.
Defines the 8 annual report sections — each with a retrieval_prompt and summary_prompt.
This is the single source of truth for section labels and prompts across the entire app.
"""

ANNUAL_REPORT_SECTIONS = {

    "business_information": {
        "label": "Business Information",
        "retrieval_prompt": (
            "business model, products and services, company operations, "
            "market segments, operational geography, strategic direction, "
            "core business activities, value proposition, industry verticals, "
            "revenue streams, business overview, what the company does"
        ),
        "summary_prompt": (
            "Summarize the company's business model and core operations. "
            "Cover: the products and services offered, key market segments, "
            "operational geographies, and the company's strategic direction. "
            "Highlight any unique value proposition or competitive differentiator. "
            "Add one insight on how the business model is positioned for long-term resilience. "
            "(Target: ~150 words)"
        )
    },

    "corporate_information": {
        "label": "Corporate Information",
        "retrieval_prompt": (
            "board of directors, top management, leadership team, "
            "statutory auditors, secretarial auditors, legal advisors, "
            "bankers, registered office, corporate directory, "
            "key managerial personnel, company secretary, CFO"
        ),
        "summary_prompt": (
            "Summarize the company's corporate directory. "
            "Include: key board members and their designations, top management, "
            "statutory and secretarial auditors, legal advisors, and banking partners. "
            "Note any significant appointments or changes in leadership during the year. "
            "Add one insight on the depth and experience of the leadership bench. "
            "(Target: ~150 words)"
        )
    },

    "chairmans_message": {
        "label": "Chairman's Message",
        "retrieval_prompt": (
            "chairman message, chairman's letter, dear shareholders, "
            "managing director letter, founder message, board chairman address, "
            "letter to shareholders, annual message from leadership, "
            "vision statement, highlights of the year, our journey, "
            "message from the desk of chairman"
        ),
        "summary_prompt": (
            "Summarize the Chairman's message to shareholders. "
            "Capture: the overall tone (optimistic/cautious), key achievements highlighted, "
            "challenges acknowledged, the company's vision, and the strategic outlook communicated. "
            "Note any direct commitments made to stakeholders. "
            "Add one thought-provoking insight about the leadership's stated vision vs. ground realities. "
            "(Target: ~150 words)"
        )
    },

    "boards_report": {
        "label": "Board's Report",
        "retrieval_prompt": (
            "board's report, directors report, statutory disclosures, "
            "management report, compliance report, related party transactions, "
            "dividend declaration, corporate performance, board activities, "
            "internal financial controls, auditor observations, CSR activities"
        ),
        "summary_prompt": (
            "Summarize the Board's Report. "
            "Cover: the board's assessment of corporate performance, key statutory disclosures, "
            "related party transactions, dividend decisions, CSR activities, "
            "and any auditor observations or qualifications. "
            "Flag any governance concerns or regulatory non-compliance mentioned. "
            "Add one insight on what the board's disclosures reveal about management accountability. "
            "(Target: ~150 words)"
        )
    },

    "shareholding_information": {
        "label": "Shareholding Information",
        "retrieval_prompt": (
            "shareholding pattern, promoter holdings, public shareholders, "
            "institutional investors, FII holdings, DII holdings, "
            "ownership structure, equity shares, share capital, "
            "top shareholders, retail investors, demat shares"
        ),
        "summary_prompt": (
            "Summarize the company's shareholding structure. "
            "Include: promoter vs. public holding percentages, institutional investor presence "
            "(FII/DII), any notable changes in ownership during the year, "
            "and the concentration or distribution of equity. "
            "Add one insight on what the ownership pattern signals about investor confidence or control risk. "
            "(Target: ~150 words)"
        )
    },

    "corporate_governance": {
        "label": "Corporate Governance",
        "retrieval_prompt": (
            "corporate governance, board committees, audit committee, "
            "nomination remuneration committee, SEBI compliance, governance practices, "
            "board independence, ethics policy, whistleblower policy, "
            "director independence, board diversity, executive compensation"
        ),
        "summary_prompt": (
            "Summarize the corporate governance framework. "
            "Include: board composition and independence, key committees and their roles, "
            "SEBI compliance status, ethics and whistleblower policies, "
            "and executive compensation highlights. "
            "Note any governance lapses or improvements flagged during the year. "
            "Add one insight on the quality and transparency of governance practices. "
            "(Target: ~150 words)"
        )
    },

    "mda": {
        "label": "Management Discussion & Analysis",
        "retrieval_prompt": (
            "management discussion and analysis, MD&A, industry outlook, "
            "business performance, segment performance, macroeconomic environment, "
            "financial health, operational review, risks and concerns, "
            "opportunities, threats, future plans, management commentary"
        ),
        "summary_prompt": (
            "Summarize the Management Discussion & Analysis section. "
            "Cover: management's view on industry trends, segment-wise performance, "
            "key financial metrics discussed, identified risks and opportunities, "
            "and the company's plans for the near future. "
            "Add one insight on any gap between the management's narrative and the actual reported numbers. "
            "(Target: ~150 words)"
        )
    },

    "financial_statements": {
        "label": "Consolidated Financial Statements",
        "retrieval_prompt": (
            "consolidated financial statements, balance sheet, profit and loss, "
            "income statement, cash flow statement, revenue, net profit, EBITDA, "
            "total assets, total liabilities, earnings per share, return on equity, "
            "financial highlights, key financial ratios, net worth, borrowings"
        ),
        "summary_prompt": (
            "Summarize the key figures from the consolidated financial statements. "
            "Include: revenue, net profit/loss, EBITDA, total assets, net worth, "
            "EPS, and year-over-year growth percentages where available. "
            "Highlight any significant balance sheet changes or exceptional items. "
            "Be numerically precise — cite actual figures wherever present. "
            "Add one insight on what the financials collectively reveal about the company's growth trajectory. "
            "(Target: ~150 words)"
        )
    }

}

# Convenience: ordered list of section keys matching display order
SECTION_ORDER = list(ANNUAL_REPORT_SECTIONS.keys())