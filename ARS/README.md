## Annual Report Summarizer (ARS)

Annual Report Summarizer is a full-stack AI application that ingests annual report PDFs, generates section-wise summaries, and enables deeper analysis through translation, audio playback, cross-year comparison, and report-grounded chat.

The project is split into:

- `backend` (FastAPI + LangChain + ChromaDB)
- `frontend` (React + Vite)

---

## What This Project Does

After uploading a company annual report PDF for a specific year, ARS can:

- Extract and chunk report content
- Build and persist vector embeddings for retrieval
- Generate summaries across eight annual report sections
- Re-summarize a report later without re-uploading the PDF
- Compare two report years and generate delta insights
- Translate summaries to multiple languages
- Generate audio narration (section-level or full report)
- Answer follow-up questions in a contextual chat session

---

## Core Features

1. Authentication
- Local sign-up/sign-in with JWT
- Google OAuth sign-in
- Session restore and route protection in frontend

2. Report Ingestion Pipeline
- Upload PDF + company + year
- Background job execution with polling (`queued`, `running`, `done`, `error`)
- Optional force re-index / re-summarize flags

3. Section-wise Summaries
- Returns summaries with labels and generation timestamp
- Stored on disk for reuse
- One-click re-summarize from cached retrieval artifacts

4. Compare Years
- Select two years for the same company
- Get executive delta + section-level improvements/declines/new developments

5. Translation
- Translate all section summaries to supported languages

6. Audio Generation
- Convert one section or complete report summary into MP3
- Served from backend static audio endpoint

7. Chat with Reports
- Ask questions against a specific company-year report
- Persistent per-report session history
- Clear chat history on demand

8. Artifact Management
- List all processed reports
- Delete all artifacts for a company-year (summaries, vector store, chunks, chat history, audio)

---

## Tech Stack

Frontend:

- React 18
- React Router
- Axios
- Vite

Backend:

- FastAPI
- Uvicorn
- LangChain ecosystem
- ChromaDB
- HuggingFace embeddings
- Groq LLM integration
- gTTS for audio
- Deep Translator for multilingual support

---

## Project Structure

```
ARS/
	backend/
		api/            # FastAPI route modules
		auth/           # JWT + Google OAuth logic
		core/           # Pipeline, summarizer, retriever, chat, translation, audio
		data/           # Persisted app data (summaries, chunks, chroma, chat, audio, uploads)
		main.py         # FastAPI app entrypoint
	frontend/
		src/pages/      # Login, Dashboard, ReportView, Compare
		src/components/ # UI components by feature
		src/api/        # Axios API client
		vite.config.js  # Dev server + backend proxy
```

---

## Prerequisites

- Python 3.10+ recommended
- Node.js 18+ recommended
- npm
- Internet access for LLM, translation, and Google OAuth flows

---

## Environment Variables

Create `backend/.env` with the following values:

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | API key used for report summarization/comparison/chat model calls |
| `HF_API_KEY` | Optional (recommended) | Hugging Face access key for embedding model downloads |
| `JWT_SECRET_KEY` | Yes | Secret used to sign/verify JWT tokens |
| `FRONTEND_URL` | Yes | Frontend base URL (default: `http://localhost:5173`) |
| `BACKEND_URL` | Yes | Backend base URL (default: `http://localhost:8000`) |
| `GOOGLE_CLIENT_ID` | Optional | Needed only if using Google OAuth login |
| `GOOGLE_CLIENT_SECRET` | Optional | Needed only if using Google OAuth login |

Minimal local `.env` example:

```env
GROQ_API_KEY=your_groq_api_key
HF_API_KEY=your_hf_api_key
JWT_SECRET_KEY=replace_with_a_long_random_secret

FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000

GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

If you do not need Google OAuth, local email/password authentication still works.

---

## Installation

### 1) Clone and enter the project

```bash
git clone <your-repository-url>
cd ARS
```

### 2) Backend setup

```bash
cd backend
python -m venv venv
```

Activate virtual environment:

- Windows (PowerShell):

```powershell
venv\Scripts\Activate
```

- macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3) Frontend setup

```bash
cd ../frontend
npm install
```

---

## Running the Project

You need two terminals.

### Terminal A: Start backend

From `ARS/backend`:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend URLs:

- API root: `http://localhost:8000/`
- Swagger docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Terminal B: Start frontend

From `ARS/frontend`:

```bash
npm run dev
```

Frontend URL:

- App: `http://localhost:5173`

Vite proxies `/api` and `/audio-files` requests to the backend.

---

## Typical User Flow

1. Sign in (local account or Google OAuth).
2. Upload annual report PDF on Dashboard with company and year.
3. Wait for pipeline completion.
4. Open report view to read section summaries.
5. Optionally translate summaries, generate audio, or ask chat questions.
6. Compare two years for the same company in Compare view.
7. Use Resummarize when you want fresh summaries from cached artifacts.

---

## Data Persistence

Generated artifacts are stored under `backend/data/`:

- `summaries/` for summary JSON files
- `chunks/` for chunk snapshots
- `chroma_store/` for vector index collections
- `chat_history/` for per-report conversations
- `audio/` for generated MP3 files
- `uploads/` for uploaded PDFs

This makes repeated access fast and enables re-summarization without re-uploading files.

---

## Main API Groups

- `/auth` - sign-up/sign-in, Google OAuth, current user
- `/reports` - list reports, delete report artifacts
- `/pipeline` - upload + run processing job, poll status
- `/summaries` - fetch summaries, re-summarize cached report
- `/translate` - get supported languages, translate summaries
- `/audio` - generate summary audio files
- `/compare` - cross-year delta analysis
- `/chat` - ask report questions, clear chat history

---

## Troubleshooting

1. Frontend cannot reach backend
- Ensure backend runs on `http://localhost:8000`
- Ensure frontend runs on `http://localhost:5173`
- Confirm Vite proxy configuration in `frontend/vite.config.js`

2. `401 Unauthorized` errors
- Token may be expired/invalid; sign in again
- Confirm `JWT_SECRET_KEY` is set and stable

3. Pipeline or model failures
- Verify `GROQ_API_KEY`
- Confirm internet connectivity for external model services

4. Google OAuth fails
- Ensure `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are correct
- Add exact callback URL in Google console: `http://localhost:8000/auth/callback`

5. Audio generation issues
- Ensure translation/language code is valid and summary text exists

---

## Notes

- The in-memory pipeline job store resets on backend restart.
- This project is suitable for local development and demos; production deployment should add persistent job queues, hardened secret management, and stronger operational safeguards.

