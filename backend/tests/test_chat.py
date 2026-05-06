import io
import pytest

pytestmark = pytest.mark.asyncio


async def test_stream_with_docs(client, auth, sample_pdf):
    await client.post("/documents/upload", headers=auth,
        files={"file": ("doc.pdf", io.BytesIO(sample_pdf), "application/pdf")})
    r = await client.post("/chat/stream", headers={**auth, "Accept": "text/event-stream"},
        json={"query": "What is this about?"})
    assert r.status_code == 200
    assert "text/event-stream" in r.headers["content-type"]
    assert "data:" in r.text


async def test_stream_no_docs(client, auth, monkeypatch):
    monkeypatch.setattr("app.routes.chat.search", lambda q, **kw: [])
    r = await client.post("/chat/stream", headers={**auth, "Accept": "text/event-stream"},
        json={"query": "hello"})
    assert r.status_code == 200
    assert "No relevant documents" in r.text


async def test_stream_no_auth(client):
    r = await client.post("/chat/stream", json={"query": "hello"})
    assert r.status_code in (401, 403)


async def test_stream_empty_query(client, auth):
    r = await client.post("/chat/stream", headers=auth, json={})
    assert r.status_code == 422


async def test_stream_with_doc_ids(client, auth, sample_pdf):
    up = await client.post("/documents/upload", headers=auth,
        files={"file": ("doc.pdf", io.BytesIO(sample_pdf), "application/pdf")})
    doc_id = up.json()["id"]
    r = await client.post("/chat/stream", headers={**auth, "Accept": "text/event-stream"},
        json={"query": "Summarize", "doc_ids": [doc_id]})
    assert r.status_code == 200
