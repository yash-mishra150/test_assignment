import io
import pytest

pytestmark = pytest.mark.asyncio


async def test_upload_audio(client, auth, mp3_bytes):
    r = await client.post("/media/upload", headers=auth,
        files={"file": ("audio.mp3", io.BytesIO(mp3_bytes), "audio/mpeg")})
    assert r.status_code == 201
    assert r.json()["doc_type"] == "audio"
    assert r.json()["summary"] == "Test summary."


async def test_upload_video(client, auth):
    r = await client.post("/media/upload", headers=auth,
        files={"file": ("video.mp4", io.BytesIO(b"\x00" * 100), "video/mp4")})
    assert r.status_code == 201
    assert r.json()["doc_type"] == "video"


async def test_upload_unsupported(client, auth):
    r = await client.post("/media/upload", headers=auth,
        files={"file": ("doc.docx", io.BytesIO(b"data"), "application/vnd.openxmlformats")})
    assert r.status_code == 400


async def test_upload_empty(client, auth):
    r = await client.post("/media/upload", headers=auth,
        files={"file": ("empty.mp3", io.BytesIO(b""), "audio/mpeg")})
    assert r.status_code == 400


async def test_transcript(client, auth, mp3_bytes):
    up = await client.post("/media/upload", headers=auth,
        files={"file": ("a.mp3", io.BytesIO(mp3_bytes), "audio/mpeg")})
    doc_id = up.json()["id"]
    r = await client.get(f"/media/{doc_id}/transcript", headers=auth)
    assert r.status_code == 200
    segs = r.json()["segments"]
    assert len(segs) == 2
    assert segs[0]["text"] == "Hello world"


async def test_transcript_not_found(client, auth):
    r = await client.get("/media/nope/transcript", headers=auth)
    assert r.status_code == 404


async def test_transcript_on_pdf(client, auth, sample_pdf):
    up = await client.post("/documents/upload", headers=auth,
        files={"file": ("doc.pdf", io.BytesIO(sample_pdf), "application/pdf")})
    doc_id = up.json()["id"]
    r = await client.get(f"/media/{doc_id}/transcript", headers=auth)
    assert r.status_code == 400


async def test_media_no_auth(client, mp3_bytes):
    r = await client.post("/media/upload",
        files={"file": ("a.mp3", io.BytesIO(mp3_bytes), "audio/mpeg")})
    assert r.status_code in (401, 403)


async def test_file_not_found(client, auth):
    r = await client.get("/media/nonexistent/file", headers=auth)
    assert r.status_code == 404


async def test_empty_transcription(client, auth, mp3_bytes, monkeypatch):
    monkeypatch.setattr("app.routes.media._transcribe", lambda path: [])
    r = await client.post("/media/upload", headers=auth,
        files={"file": ("a.mp3", io.BytesIO(mp3_bytes), "audio/mpeg")})
    assert r.status_code == 422


async def test_summarize_failure_returns_null(client, auth, mp3_bytes, monkeypatch):
    async def bad_summarize(_text):
        raise RuntimeError("Ollama down")
    monkeypatch.setattr("app.routes.media.summarize", bad_summarize)
    r = await client.post("/media/upload", headers=auth,
        files={"file": ("a.mp3", io.BytesIO(mp3_bytes), "audio/mpeg")})
    assert r.status_code == 201
    assert r.json()["summary"] is None
