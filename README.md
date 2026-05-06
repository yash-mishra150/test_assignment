# DocQA — AI-Powered Document & Multimedia Q&A

A full-stack web application that lets users upload PDF documents, audio, and video files, then ask questions using an AI chatbot with real-time streaming responses, timestamp extraction, and media playback.

---

## Features

| Feature | Detail |
|---|---|
| PDF Q&A | Upload PDFs, get AI summaries and ask questions |
| Audio/Video Q&A | Transcribe media with faster-whisper, extract timestamps |
| Semantic Search | FAISS vector search using sentence-transformers embeddings |
| Streaming Chat | Real-time SSE token streaming from Ollama (qwen3.5:9b) |
| Timestamp Playback | Click a source badge in chat → media player seeks to that moment |
| Multi-user Auth | JWT access + refresh tokens, per-user document isolation |
| Rate Limiting | 20 requests/min per IP via slowapi + Redis |
| Response Caching | Redis caches chat answers for 5 minutes |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.13) |
| LLM | Ollama — `qwen3.5:9b` (runs on your host, not in Docker) |
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` |
| Vector Store | FAISS (persisted to volume) |
| Transcription | faster-whisper (CPU, `base` model) |
| Database | SQLite via aiosqlite (embedded, zero infra) |
| Rate-limiting | Redis `7-alpine` (~30 MB) via slowapi |
| Response cache | In-process TTL dict (no Redis dependency) |
| Frontend | React 18 + TypeScript + TailwindCSS + Vite |
| Containers | Docker + Docker Compose (3 services) |
| CI/CD | GitHub Actions |

---

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose v2
- [Ollama](https://ollama.com/) installed and running on your machine (not in Docker)

### 1. Clone and configure

```bash
git clone <your-repo-url>
cd docqa
cp backend/.env.example backend/.env
# Edit backend/.env — at minimum set a real JWT_SECRET
```

### 2. Pull the LLM model

```bash
ollama pull qwen3.5:9b
```

### 3. Start the stack

```bash
docker compose up --build
```

Services started: **backend**, **frontend**, **redis** (3 total — MongoDB and Ollama not in Docker).

| Service | URL |
|---|---|
| Frontend | http://localhost |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

### 4. First use

1. Open http://localhost and create an account
2. Upload a PDF, MP3, WAV, or MP4 file
3. Wait for the AI summary to appear
4. Select the file with the checkbox → ask questions in the chat
5. For audio/video: click timestamp badges to jump to the relevant moment

---

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

---

## Running Tests

### Backend (requires venv active)

```bash
cd backend
source venv/bin/activate
pytest
```

Coverage report is generated in `backend/htmlcov/index.html`. The suite enforces **≥ 95% coverage** and will fail below that threshold.

### Frontend

```bash
cd frontend
npm test
```

---

## API Documentation

Full interactive docs at **http://localhost:8000/docs** (Swagger UI).

### Auth endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/register` | Create account |
| `POST` | `/auth/login` | Login → access + refresh tokens |
| `POST` | `/auth/refresh` | Rotate tokens |

### Document endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/documents/upload` | Upload PDF (multipart) |
| `GET` | `/documents/` | List user's documents |
| `GET` | `/documents/{id}` | Get document metadata + summary |

### Media endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/media/upload` | Upload audio or video |
| `GET` | `/media/{id}/transcript` | Get transcript with timestamps |
| `GET` | `/media/{id}/file` | Stream raw media file |

### Chat endpoint

| Method | Path | Description |
|---|---|---|
| `POST` | `/chat/query` | SSE streaming RAG chat |

**Chat request body:**
```json
{
  "query": "What are the key findings?",
  "doc_ids": ["<doc_id_1>", "<doc_id_2>"]
}
```

**SSE event types:**
- `event: token` — streamed answer token
- `event: sources` — JSON array of source references (with timestamps for media)
- `event: done` — stream complete

---

## Project Structure

```
docqa/
├── backend/
│   ├── app/
│   │   ├── api/routes/     # auth, documents, media, chat
│   │   ├── core/           # config, JWT/security
│   │   ├── db/             # MongoDB client, FAISS store
│   │   ├── models/         # Pydantic schemas
│   │   ├── services/       # LLM, embeddings, PDF, transcription, cache
│   │   └── main.py         # FastAPI app
│   ├── tests/              # pytest test suite (≥95% coverage)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # FileUpload, ChatInterface, MediaPlayer, etc.
│   │   ├── hooks/          # useChat, useFileUpload
│   │   ├── pages/          # Login, Dashboard
│   │   └── services/api.ts # Axios + SSE client
│   └── Dockerfile
├── .github/workflows/      # CI (test + coverage) + build (Docker push)
└── docker-compose.yml
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SQLITE_PATH` | `/data/docqa.db` | SQLite database file path |
| `REDIS_URL` | `redis://redis:6379` | Redis URL (rate-limiting only) |
| `OLLAMA_URL` | `http://host.docker.internal:11434` | Ollama server URL (host machine) |
| `OLLAMA_MODEL` | `qwen3.5:9b` | Model name to use |
| `JWT_SECRET` | *(required)* | Secret for signing JWTs |
| `FAISS_INDEX_PATH` | `/data/faiss.index` | Where to persist the FAISS index |
| `MEDIA_STORAGE_PATH` | `/data/media` | Where to store uploaded media files |
| `RATE_LIMIT_PER_MINUTE` | `20` | Chat requests per minute per IP |

---

## CI/CD

GitHub Actions runs on every push and pull request:

1. **Backend tests** — pytest with ≥95% coverage gate (SQLite in-memory, no external services needed)
2. **Frontend tests** — Vitest + TypeScript type check + production build
3. **Docker build** — validates both images build successfully

On tagged releases (`v*`), images are pushed to Docker Hub (requires `DOCKER_USERNAME` / `DOCKER_PASSWORD` secrets).

---

## Demo Walkthrough

> Record a video walkthrough and add the YouTube/Google Drive link here.

**Suggested walkthrough outline:**
1. Register → login
2. Upload a PDF → show summary
3. Ask a question → show streaming response with page citations
4. Upload an MP3 → show transcript timestamps
5. Ask a question about the audio → click timestamp badge → media seeks
6. Show test coverage report
7. Show GitHub Actions CI run
