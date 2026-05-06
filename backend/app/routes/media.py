import os
from datetime import datetime, timezone
from uuid import uuid4

import aiosqlite
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.database import get_db
from app.rag import add_documents, summarize
from app.routes.auth import current_user

router = APIRouter(prefix="/media", tags=["media"])
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)

AUDIO = {"audio/mpeg", "audio/wav", "audio/x-wav", "audio/ogg", "audio/mp3"}
VIDEO = {"video/mp4", "video/webm", "video/quicktime", "video/x-msvideo"}
ALLOWED = AUDIO | VIDEO


def _transcribe(path: str):
    from faster_whisper import WhisperModel
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(path)
    return [{"start": s.start, "end": s.end, "text": s.text.strip()} for s in segments]


@router.post("/upload", status_code=201)
async def upload(file: UploadFile = File(...), user: dict = Depends(current_user)):
    if file.content_type not in ALLOWED:
        raise HTTPException(400, "Unsupported file type")
    data = await file.read()
    if not data:
        raise HTTPException(400, "Empty file")

    doc_id = str(uuid4())
    settings.media_dir.mkdir(parents=True, exist_ok=True)
    ext = os.path.splitext(file.filename)[-1]
    file_path = str(settings.media_dir / f"{doc_id}{ext}")
    with open(file_path, "wb") as f:
        f.write(data)

    segments = _transcribe(file_path)
    if not segments:
        raise HTTPException(422, "Could not transcribe file")

    full_text = " ".join(s["text"] for s in segments)
    doc_type = "audio" if file.content_type in AUDIO else "video"

    # Build chunks with timestamp metadata
    chunks = []
    for s in segments:
        chunks.append(Document(
            page_content=s["text"],
            metadata={
                "doc_id": doc_id, "user_id": user["id"],
                "source": file.filename,
                "start_sec": s["start"], "end_sec": s["end"],
            },
        ))
    add_documents(chunks)

    try:
        summary = await summarize(full_text)
    except Exception:
        summary = None

    now = datetime.now(timezone.utc).isoformat()
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        await db.execute(
            "INSERT INTO documents VALUES (?,?,?,?,?,?,?)",
            (doc_id, user["id"], file.filename, doc_type, summary, file_path, now),
        )
        await db.executemany(
            "INSERT INTO segments (doc_id, start, end_time, text) VALUES (?,?,?,?)",
            [(doc_id, s["start"], s["end"], s["text"]) for s in segments],
        )
        await db.commit()

    return {"id": doc_id, "filename": file.filename, "doc_type": doc_type, "summary": summary}


@router.get("/{doc_id}/transcript")
async def transcript(doc_id: str, user: dict = Depends(current_user)):
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT doc_type FROM documents WHERE id=? AND user_id=?", (doc_id, user["id"])
        ) as c:
            doc = await c.fetchone()
        if not doc:
            raise HTTPException(404, "Not found")
        if doc["doc_type"] not in ("audio", "video"):
            raise HTTPException(400, "Not a media file")
        async with db.execute(
            "SELECT start, end_time, text FROM segments WHERE doc_id=? ORDER BY start", (doc_id,)
        ) as c:
            segs = [dict(r) for r in await c.fetchall()]
    return {"doc_id": doc_id, "segments": segs}


@router.get("/{doc_id}/file")
async def get_file(doc_id: str, user: dict = Depends(current_user)):
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT filename, file_path FROM documents WHERE id=? AND user_id=?", (doc_id, user["id"])
        ) as c:
            row = await c.fetchone()
    if not row or not row["file_path"] or not os.path.exists(row["file_path"]):
        raise HTTPException(404, "File not found")
    return FileResponse(row["file_path"], filename=row["filename"])
