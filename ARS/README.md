<div align="center">

# Annual Report Summarizer

**Transform dense financial PDFs into actionable intelligence — in seconds.**

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React_18-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6F61?style=for-the-badge)](https://www.trychroma.com)
[![Groq](https://img.shields.io/badge/Groq_LLM-F55036?style=for-the-badge)](https://groq.com)
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)

</div>

---

## ✦ What is ARS?

> *ARS is a full-stack AI application that ingests annual report PDFs and turns them into structured summaries, multilingual translations, audio narrations, cross-year comparisons, and a contextual chat interface — all powered by retrieval-augmented generation.*

Upload a PDF. Get intelligence.

---

## ⚡ Feature Overview

<table>
<thead>
  <tr>
    <th>🔧 Feature</th>
    <th>📋 What it does</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td><strong>🔐 Authentication</strong></td>
    <td>Local JWT sign-up/sign-in + Google OAuth with session restore and route protection</td>
  </tr>
  <tr>
    <td><strong>📥 Report Ingestion</strong></td>
    <td>Upload PDF with company & year; background pipeline with live status polling (<code>queued → running → done</code>)</td>
  </tr>
  <tr>
    <td><strong>📑 Section Summaries</strong></td>
    <td>Auto-generates summaries across <strong>8 report sections</strong>; cached for instant reuse</td>
  </tr>
  <tr>
    <td><strong>📊 Year Comparison</strong></td>
    <td>Cross-year delta analysis — improvements, declines, and new developments at section level</td>
  </tr>
  <tr>
    <td><strong>🌐 Translation</strong></td>
    <td>Translate all section summaries to any supported language instantly</td>
  </tr>
  <tr>
    <td><strong>🎙️ Audio Narration</strong></td>
    <td>Convert one section or the full report summary into an MP3 file</td>
  </tr>
  <tr>
    <td><strong>💬 Chat Interface</strong></td>
    <td>Ask natural-language questions grounded in the uploaded report, with persistent chat history</td>
  </tr>

</tbody>
</table>

---

## 🏗️ Architecture

```
ARS/
├── 🖥️  backend/
│   ├── api/            ← FastAPI route modules
│   ├── auth/           ← JWT + Google OAuth logic
│   ├── core/           ← Pipeline, summarizer, retriever, chat, translation, audio
│   ├── data/           ← Persisted app data (summaries, chunks, chroma, chat, audio, uploads)
│   └── main.py         ← FastAPI app entrypoint
│
└── 🌐  frontend/
    ├── src/
    │   ├── pages/      ← Login, Dashboard, ReportView, Compare
    │   ├── components/ ← UI components by feature
    │   └── api/        ← Axios API client
    └── vite.config.js  ← Dev server + backend proxy
```

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 18, React Router, Axios, Vite |
| **Backend** | FastAPI, Uvicorn, LangChain ecosystem |
| **AI / ML** | Groq LLM, HuggingFace Embeddings, ChromaDB |
| **Utilities** | gTTS (audio), Deep Translator (multilingual) |

---

## 🚀 Getting Started

### Prerequisites

Before you begin, make sure you have:

- 🐍 **Python 3.10+**
- 🟢 **Node.js 18+** & **npm**
- 🌐 **Internet access** (for LLM, translation, and OAuth flows)

---

### Step 1 — Clone the Repository

```bash
git clone <your-repository-url>
cd ARS
```

---

### Step 2 — Configure Environment Variables

Create a `.env` file inside the `backend/` directory:

```env
# ── Required ─────────────────────────────────────────
GROQ_API_KEY=your_groq_api_key
JWT_SECRET_KEY=replace_with_a_long_random_secret

FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000

# ── Recommended ──────────────────────────────────────
HF_API_KEY=your_hf_api_key

# ── Optional (Google OAuth only) ─────────────────────
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

> 💡 **Tip:** Google OAuth is entirely optional. Local email/password authentication works out of the box.

<details>
<summary>📋 Full Environment Variable Reference</summary>

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | API key for summarization, comparison, and chat model calls |
| `HF_API_KEY` | ⚡ Recommended | Hugging Face key for embedding model downloads |
| `JWT_SECRET_KEY` | ✅ Yes | Secret used to sign/verify JWT tokens |
| `FRONTEND_URL` | ✅ Yes | Frontend base URL (default: `http://localhost:5173`) |
| `BACKEND_URL` | ✅ Yes | Backend base URL (default: `http://localhost:8000`) |
| `GOOGLE_CLIENT_ID` | 🔘 Optional | Needed only for Google OAuth login |
| `GOOGLE_CLIENT_SECRET` | 🔘 Optional | Needed only for Google OAuth login |

</details>

---

### Step 3 — Backend Setup

```bash
cd backend
python -m venv venv
```

**Activate the virtual environment:**

```bash
# macOS / Linux
source venv/bin/activate

# Windows (PowerShell)
venv\Scripts\Activate
```

**Install dependencies:**

```bash
pip install -r requirements.txt
```

---

### Step 4 — Frontend Setup

```bash
cd ../frontend
npm install
```

---

### Step 5 — Run the Application

Open **two terminals** and run each simultaneously:

**Terminal A — Backend**
```bash
# From ARS/backend/
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal B — Frontend**
```bash
# From ARS/frontend/
npm run dev
```

| Service | URL |
|---------|-----|
| 🌐 App | http://localhost:5173 |
| 📡 API Root | http://localhost:8000/ |
| 📖 Swagger Docs | http://localhost:8000/docs |
| 📘 ReDoc | http://localhost:8000/redoc |

> Vite automatically proxies `/api` and `/audio-files` to the backend.

---

## 🗺️ Typical User Flow

```
1. 🔑  Sign in  →  local account or Google OAuth
        │
2. 📤  Upload   →  annual report PDF with company name & year
        │
3. ⏳  Wait     →  pipeline runs in background (queued → running → done)
        │
4. 📖  Read     →  explore 8 section-wise summaries in Report View
        │
5. ✨  Enhance  →  translate · generate audio · ask chat questions
        │
6. 📊  Compare  →  select two years → get delta insights
        │
7. 🔄  Refresh  →  re-summarize from cached artifacts anytime
```

---

## 💾 Data Persistence

All generated artifacts are stored under `backend/data/`:

```
backend/data/
├── 📝 summaries/       ← Section summary JSON files
├── 🧩 chunks/          ← Chunked document snapshots
├── 🔍 chroma_store/    ← Vector index collections
├── 💬 chat_history/    ← Per-report conversation logs
├── 🔊 audio/           ← Generated MP3 narrations
└── 📄 uploads/         ← Original uploaded PDFs
```

> This makes repeated access fast and enables re-summarization without re-uploading files.

---

## 🔌 API Reference

| Group | Endpoints |
|-------|-----------|
| `/auth` | Sign-up, sign-in, Google OAuth, current user |
| `/reports` | List reports, delete report artifacts |
| `/pipeline` | Upload + run processing job, poll job status |
| `/summaries` | Fetch summaries, re-summarize cached report |
| `/translate` | Get supported languages, translate summaries |
| `/audio` | Generate and serve MP3 summary audio |
| `/compare` | Cross-year delta analysis |
| `/chat` | Ask report questions, clear chat history |

---

## 🩺 Troubleshooting

<details>
<summary>🔴 Frontend cannot reach backend</summary>

- Ensure backend runs on `http://localhost:8000`
- Ensure frontend runs on `http://localhost:5173`
- Confirm Vite proxy configuration in `frontend/vite.config.js`
</details>

<details>
<summary>🔴 401 Unauthorized errors</summary>

- Token may be expired or invalid — sign in again
- Confirm `JWT_SECRET_KEY` is set and hasn't changed between restarts
</details>

<details>
<summary>🔴 Pipeline or model failures</summary>

- Verify `GROQ_API_KEY` is correct and active
- Confirm internet connectivity for external model services
</details>

<details>
<summary>🔴 Google OAuth not working</summary>

- Ensure `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are correct
- Add the exact callback URL in your Google Console:
  ```
  http://localhost:8000/auth/callback
  ```
</details>

<details>
<summary>🔴 Audio generation issues</summary>

- Ensure the target language code is valid
- Verify that summary text exists for the selected section
</details>

---

## ⚠️ Important Notes

> **Pipeline Job Store** — The in-memory job store resets on every backend restart. Re-submit any interrupted jobs after restarting.

> **Production Readiness** — This project is optimized for local development and demos. For production, add: persistent job queues, hardened secret management, rate limiting, and stronger operational safeguards.

---

<div align="center">

Built with 🤖 AI · ⚡ Speed · 📊 Purpose

*ARS — because annual reports shouldn't take all year.*

</div>
