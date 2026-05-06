import time
import logging
from datetime import datetime, timezone
from uuid import uuid4

import aiosqlite
import fitz
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.database import get_db
from app.rag import add_documents, summarize
from app.routes.auth import current_user

router = APIRouter(prefix="/documents", tags=["documents"])
# all-minilm has 256-token context limit (~500 chars of typical text)
splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
log = logging.getLogger("docqa")


def _extract_text(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = "\n\n".join(page.get_text() for page in doc)
    doc.close()
    return text


@router.post("/upload", status_code=201)
async def upload(file: UploadFile = File(...), user: dict = Depends(current_user)):
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF files are supported")
    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(400, "Empty file")

    t0 = time.perf_counter()

    text = _extract_text(pdf_bytes)
    if not text.strip():
        raise HTTPException(422, "No text found in PDF")
    log.info(f"[upload] extract_text: {time.perf_counter()-t0:.2f}s")

    doc_id = str(uuid4())
    chunks = splitter.create_documents(
        [text],
        metadatas=[{"doc_id": doc_id, "user_id": user["id"], "source": file.filename}],
    )
    log.info(f"[upload] chunked into {len(chunks)} chunks")

    t1 = time.perf_counter()
    add_documents(chunks)
    log.info(f"[upload] embed+index: {time.perf_counter()-t1:.2f}s")

    t2 = time.perf_counter()
    try:
        summary = await summarize(text)
        log.info(f"[upload] summarize: {time.perf_counter()-t2:.2f}s")
    except Exception as e:
        log.warning(f"[upload] summarize failed: {e}")
        summary = None

    log.info(f"[upload] TOTAL: {time.perf_counter()-t0:.2f}s")

    now = datetime.now(timezone.utc).isoformat()
    async with get_db() as db:
        await db.execute(
            "INSERT INTO documents VALUES (?,?,?,?,?,?,?)",
            (doc_id, user["id"], file.filename, "pdf", summary, None, now),
        )
        await db.commit()

    return {"id": doc_id, "filename": file.filename, "doc_type": "pdf", "summary": summary}


@router.get("/")
async def list_docs(user: dict = Depends(current_user)):
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM documents WHERE user_id=? ORDER BY created_at DESC", (user["id"],)
        ) as c:
            return [dict(r) for r in await c.fetchall()]


@router.get("/{doc_id}")
async def get_doc(doc_id: str, user: dict = Depends(current_user)):
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM documents WHERE id=? AND user_id=?", (doc_id, user["id"])
        ) as c:
            row = await c.fetchone()
    if not row:
        raise HTTPException(404, "Not found")
    return dict(row)
