import io
import os
import pytest
from unittest.mock import MagicMock
from httpx import AsyncClient, ASGITransport
from langchain_core.documents import Document

os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("DATA_DIR", "/tmp/docqa_test")


@pytest.fixture(autouse=True)
def patch_data_dir(tmp_path, monkeypatch):
    import app.config as _cfg
    # Routes import get_db directly, so just patch data_dir —
    # the original get_db derives its path from settings.data_dir automatically
    monkeypatch.setattr(_cfg.settings, "data_dir", tmp_path)


@pytest.fixture(autouse=True)
def patch_rag(monkeypatch):
    fake_doc = Document(
        page_content="Test content about the document.",
        metadata={"doc_id": "doc1", "user_id": "u1", "source": "test.pdf"},
    )
    monkeypatch.setattr("app.rag.add_documents", lambda docs: None)
    monkeypatch.setattr("app.rag.search", lambda q, **kw: [fake_doc])
    monkeypatch.setattr("app.rag.get_store", lambda: MagicMock())

    async def fake_summarize(_text):
        return "Test summary."

    async def fake_stream(_query, _docs):
        for tok in ["Hello ", "world."]:
            yield tok

    monkeypatch.setattr("app.rag.summarize", fake_summarize)
    monkeypatch.setattr("app.rag.stream_answer", fake_stream)
    monkeypatch.setattr("app.routes.documents.summarize", fake_summarize)
    monkeypatch.setattr("app.routes.media.summarize", fake_summarize)
    monkeypatch.setattr("app.routes.chat.search", lambda q, **kw: [fake_doc])
    monkeypatch.setattr("app.routes.chat.stream_answer", fake_stream)


@pytest.fixture(autouse=True)
def patch_whisper(monkeypatch):
    fake_segs = [
        {"start": 0.0, "end": 5.0, "text": "Hello world"},
        {"start": 5.0, "end": 10.0, "text": "This is a test"},
    ]
    monkeypatch.setattr("app.routes.media._transcribe", lambda path: fake_segs)


@pytest.fixture(autouse=True)
async def reset_sse():
    import asyncio
    from sse_starlette.sse import AppStatus
    AppStatus.should_exit = False
    AppStatus.should_exit_event = asyncio.Event()
    yield


@pytest.fixture
def sample_pdf():
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "This is a test PDF document for automated testing.")
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


@pytest.fixture
def mp3_bytes():
    return b"\xff\xfb" + b"\x00" * 200


@pytest.fixture
async def client():
    from app.main import app
    from app.database import init_db
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture
async def auth(client):
    await client.post("/auth/register", json={
        "email": "test@example.com", "password": "pass12345", "full_name": "Tester"
    })
    r = await client.post("/auth/login", json={"email": "test@example.com", "password": "pass12345"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
