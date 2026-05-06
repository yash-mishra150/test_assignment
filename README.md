# DocQA — AI-Powered Document & Multimedia Q&A

A full-stack web application that lets users upload PDF documents, audio, and video files, then ask questions using an AI chatbot with real-time streaming responses, timestamp extraction, and media playback.

---

## Demo Video

[Watch the demo on Google Drive](https://drive.google.com/file/d/1vWbi-acpRcfOFLDmL3AvUhV8ICZcVpFG/view?usp=sharing)

---

## Features

| Feature | Detail |
|---|---|
| PDF Q&A | Upload PDFs, get AI summaries and ask questions |
| Audio/Video Q&A | Transcribe media with faster-whisper, extract timestamps |
| Semantic Search | FAISS vector search using Ollama `all-minilm` embeddings |
| Streaming Chat | Real-time SSE token streaming from Ollama (`llama3.2`) |
| Timestamp Playback | Click a source badge in chat → media player seeks to that moment |
| Multi-user Auth | JWT access + refresh tokens, per-user document isolation |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.13) |
| LLM | Ollama — `llama3.2` (runs on your host, not in Docker) |
| Embeddings | Ollama — `all-minilm` |
| Vector Store | FAISS (persisted to disk) |
| Transcription | faster-whisper (CPU, `base` model) |
| Database | SQLite via aiosqlite |
| Frontend | React 18 + TypeScript + TailwindCSS + Vite |
| Containers | Docker + Docker Compose (3 services) |
| CI/CD | GitHub Actions |

---

## Quick Start (Docker)

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose v2
- [Ollama](https://ollama.com/) installed and running on your machine

### 1. Clone and configure

```bash
git clone <your-repo-url>
cd test_assignment
cp backend/.env.example backend/.env
# Edit backend/.env — set a real JWT_SECRET
```

### 2. Pull the required models

```bash
ollama pull llama3.2
ollama pull all-minilm
```

### 3. Start the stack

```bash
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

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

### Backend

```bash
cd backend
source venv/bin/activate
pytest
```

The suite has **56 tests** achieving **96.69% coverage** (enforced minimum: 95%). The HTML coverage report is generated at `backend/htmlcov/index.html`.

### Frontend

```bash
cd frontend
npm test
```

---

## API Documentation

Full interactive docs at **http://localhost:8000/docs** (Swagger UI).

### Auth

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/register` | Create account |
| `POST` | `/auth/login` | Login → access + refresh tokens |
| `POST` | `/auth/refresh` | Rotate tokens |

### Documents

| Method | Path | Description |
|---|---|---|
| `POST` | `/documents/upload` | Upload PDF (multipart) |
| `GET` | `/documents/` | List user's documents |
| `GET` | `/documents/{id}` | Get document metadata + summary |

### Media

| Method | Path | Description |
|---|---|---|
| `POST` | `/media/upload` | Upload audio or video |
| `GET` | `/media/{id}/transcript` | Get transcript with timestamps |
| `GET` | `/media/{id}/file` | Stream raw media file |

### Chat

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
test_assignment/
├── backend/
│   ├── app/
│   │   ├── routes/         # auth, documents, media, chat
│   │   ├── config.py       # settings + env vars
│   │   ├── database.py     # SQLite + FAISS
│   │   ├── rag.py          # LangChain RAG pipeline
│   │   ├── security.py     # JWT helpers
│   │   └── main.py         # FastAPI app entry point
│   ├── tests/              # pytest suite (56 tests, ≥95% coverage)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # FileUpload, ChatInterface, MediaPlayer, etc.
│   │   ├── hooks/          # useChat, useFileUpload
│   │   ├── pages/          # Login, Dashboard
│   │   └── services/       # Axios + SSE client
│   └── Dockerfile
├── .github/workflows/      # CI (test + coverage) + Docker build
└── docker-compose.yml
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server URL |
| `LLM_MODEL` | `llama3.2` | Chat model name |
| `EMBED_MODEL` | `all-minilm` | Embedding model name |
| `DATA_DIR` | `./data` | Directory for DB, FAISS index, and media files |
| `JWT_SECRET` | *(required)* | Secret for signing JWTs |

---

## CI/CD

GitHub Actions runs on every push and pull request:

1. **Backend tests** — pytest with ≥95% coverage gate
2. **Frontend tests** — Vitest + TypeScript type check + production build
3. **Docker build** — validates both images build successfully

On tagged releases (`v*`), images are pushed to Docker Hub (requires `DOCKER_USERNAME` / `DOCKER_PASSWORD` secrets).
