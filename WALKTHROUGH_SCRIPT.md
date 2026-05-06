# DocQA — Walkthrough Script
# Give this to Claude computer use / Chrome extension to execute

---

## SETUP (do before recording)

Make sure these are running before you start:

```bash
# Terminal 1 — backend
cd /Users/yashmishra/Documents/test_assignment/backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2 — frontend
cd /Users/yashmishra/Documents/test_assignment/frontend
npm run dev

# Ollama must be running
ollama serve
```

Open browser to: http://localhost:3000

---

## STEP 1 — Show the landing page (Login screen)

- Open http://localhost:3000
- The login screen appears with the DocQA branding
- Say: "This is DocQA — an AI-powered document and multimedia Q&A application built with FastAPI, React, LangChain, and Ollama running locally"

---

## STEP 2 — Register a new account

- Click "Create Account" tab
- Fill in:
  - Full Name: Demo User
  - Email: demo@example.com
  - Password: demo12345
- Click "Create Account"
- You are automatically logged in and redirected to the dashboard

---

## STEP 3 — Show the Dashboard layout

- Point out:
  - Left sidebar: document list + Upload File button
  - Middle panel: document preview / summary area
  - Right panel: chat interface
- Say: "The interface has three areas — file management on the left, document preview in the middle, and the AI chat on the right"

---

## STEP 4 — Upload a PDF

- Click "Upload File" button in the sidebar
- Drag and drop (or click to select) any PDF file — a research paper, a report, anything 2-5 pages
- Watch the upload progress bar
- After upload completes:
  - The file appears in the sidebar list
  - The middle panel shows the AI-generated **summary** of the document
- Say: "After uploading, the system automatically extracts text, creates vector embeddings using the all-minilm model via Ollama, stores them in a FAISS index, and generates a summary using qwen3.5"

---

## STEP 5 — Ask questions about the PDF (streaming chat)

- Check the checkbox next to the uploaded PDF in the sidebar to include it in chat context
- In the chat box on the right, type: "What is this document about?"
- Press Enter
- Watch the response **stream in token by token** (real-time)
- Point out the **source citation badge** at the bottom of the response showing which page it came from
- Ask a second question specific to the document content
- Say: "The chat uses RAG — Retrieval Augmented Generation. It finds the most relevant chunks from the FAISS vector store and passes them as context to the LLM, which streams the answer back via Server-Sent Events"

---

## STEP 6 — Upload an audio file

- Click "Upload File" again
- Upload an MP3 or WAV file (any audio — a podcast clip, recorded lecture, etc.)
- Wait for transcription to complete (faster-whisper runs locally on CPU)
- After upload:
  - Summary appears in the middle panel
  - The audio player appears below the summary
  - The **transcript with timestamps** appears below the player
- Say: "Audio and video files are automatically transcribed using faster-whisper, a local Whisper model. Each segment gets a timestamp."

---

## STEP 7 — Click a timestamp to seek the audio

- In the transcript list, click any timestamp entry (e.g. "0:05 — Hello world...")
- The audio player **automatically seeks** to that exact moment and starts playing
- Say: "Clicking any timestamp in the transcript seeks the audio player directly to that moment — this is the key multimedia feature of the assignment"

---

## STEP 8 — Ask a question about the audio

- Check the checkbox next to the audio file in the sidebar
- In the chat, ask a question related to what was said in the audio
- The response streams in and shows a **timestamp source badge** (e.g. "0:05 → 0:30")
- Click the timestamp badge in the chat response
- The audio player seeks to that timestamp
- Say: "When you ask about audio content, the source references include exact timestamps. Clicking them jumps the player to the relevant moment."

---

## STEP 9 — Show the API documentation

- Open a new tab: http://localhost:8000/docs
- Show the Swagger UI with all endpoints:
  - POST /auth/register, /auth/login
  - POST /documents/upload, GET /documents/
  - POST /media/upload, GET /media/{id}/transcript
  - POST /chat/stream
- Say: "The backend exposes a clean REST API with JWT authentication on every endpoint"

---

## STEP 10 — Show the test coverage

- Open a terminal
- Run:
  ```bash
  cd /Users/yashmishra/Documents/test_assignment/backend
  source venv/bin/activate
  pytest --no-cov -q
  ```
- Show 56 tests passing
- Then show the coverage:
  ```bash
  pytest -q 2>&1 | tail -5
  ```
- Show **96.69% coverage** (above the required 95%)
- Say: "The test suite has 56 tests covering auth, document upload, media upload, chat streaming, RAG pipeline, and all edge cases, achieving 96.69% code coverage"

---

## STEP 11 — Show GitHub Actions CI

- Open the GitHub repository in the browser
- Click the "Actions" tab
- Show the CI pipeline running (or already passed) with:
  - Backend tests with coverage gate
  - Frontend type check + build
  - Docker build validation
- Say: "Every push to the repository triggers the CI pipeline which enforces the 95% coverage requirement before any merge"

---

## STEP 12 — Show the project structure briefly

- Open VS Code with the project
- Briefly show:
  - `backend/app/` — FastAPI routes, RAG layer, security
  - `frontend/src/` — React components
  - `docker-compose.yml` — 3 services
  - `backend/tests/` — test suite
- Say: "The architecture is straightforward — FastAPI backend with LangChain handling the RAG pipeline, SQLite for persistence, FAISS for vector search, and a React frontend with real-time SSE streaming"

---

## CLOSING

- Return to the running app
- Say: "To summarize — DocQA supports PDF, audio, and video uploads with AI-powered Q&A, real-time streaming responses, automatic transcription, timestamp-based playback, JWT authentication, and ships with Docker Compose for easy deployment"

---

## TECH STACK TALKING POINTS

- **Backend**: FastAPI (Python), SQLite, LangChain
- **LLM**: Ollama qwen3.5:9b (runs fully locally, no API keys needed)
- **Embeddings**: Ollama all-minilm (local, 256-token context)
- **Vector Store**: FAISS (persisted to disk)
- **Transcription**: faster-whisper (local CPU)
- **Auth**: JWT tokens
- **Streaming**: Server-Sent Events (SSE)
- **Frontend**: React 18, TypeScript, TailwindCSS
- **CI/CD**: GitHub Actions
- **Containers**: Docker Compose (backend + frontend + redis)
