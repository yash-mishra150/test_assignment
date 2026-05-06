import io
import pytest

pytestmark = pytest.mark.asyncio


async def test_upload_pdf(client, auth, sample_pdf):
    r = await client.post("/documents/upload", headers=auth,
        files={"file": ("test.pdf", io.BytesIO(sample_pdf), "application/pdf")})
    assert r.status_code == 201
    data = r.json()
    assert data["doc_type"] == "pdf"
    assert data["summary"] == "Test summary."


async def test_upload_wrong_type(client, auth):
    r = await client.post("/documents/upload", headers=auth,
        files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")})
    assert r.status_code == 400


async def test_upload_empty(client, auth):
    r = await client.post("/documents/upload", headers=auth,
        files={"file": ("empty.pdf", io.BytesIO(b""), "application/pdf")})
    assert r.status_code == 400


async def test_upload_no_auth(client, sample_pdf):
    r = await client.post("/documents/upload",
        files={"file": ("test.pdf", io.BytesIO(sample_pdf), "application/pdf")})
    assert r.status_code in (401, 403)


async def test_list_empty(client, auth):
    r = await client.get("/documents/", headers=auth)
    assert r.status_code == 200
    assert r.json() == []


async def test_list_after_upload(client, auth, sample_pdf):
    await client.post("/documents/upload", headers=auth,
        files={"file": ("doc.pdf", io.BytesIO(sample_pdf), "application/pdf")})
    r = await client.get("/documents/", headers=auth)
    assert len(r.json()) == 1


async def test_get_doc(client, auth, sample_pdf):
    up = await client.post("/documents/upload", headers=auth,
        files={"file": ("doc.pdf", io.BytesIO(sample_pdf), "application/pdf")})
    doc_id = up.json()["id"]
    r = await client.get(f"/documents/{doc_id}", headers=auth)
    assert r.status_code == 200
    assert r.json()["id"] == doc_id


async def test_get_doc_not_found(client, auth):
    r = await client.get("/documents/nonexistent", headers=auth)
    assert r.status_code == 404


async def test_summarize_failure_returns_null(client, auth, sample_pdf, monkeypatch):
    async def bad_summary(_text):
        raise RuntimeError("LLM error")
    monkeypatch.setattr("app.routes.documents.summarize", bad_summary)
    r = await client.post("/documents/upload", headers=auth,
        files={"file": ("doc.pdf", io.BytesIO(sample_pdf), "application/pdf")})
    assert r.status_code == 201
    assert r.json()["summary"] is None


async def test_doc_isolation(client, sample_pdf):
    # User 1
    await client.post("/auth/register", json={"email": "u1@x.com", "password": "pass12345", "full_name": "U1"})
    t1 = (await client.post("/auth/login", json={"email": "u1@x.com", "password": "pass12345"})).json()
    h1 = {"Authorization": f"Bearer {t1['access_token']}"}
    up = await client.post("/documents/upload", headers=h1,
        files={"file": ("doc.pdf", io.BytesIO(sample_pdf), "application/pdf")})
    doc_id = up.json()["id"]

    # User 2 cannot see it
    await client.post("/auth/register", json={"email": "u2@x.com", "password": "pass12345", "full_name": "U2"})
    t2 = (await client.post("/auth/login", json={"email": "u2@x.com", "password": "pass12345"})).json()
    h2 = {"Authorization": f"Bearer {t2['access_token']}"}
    r = await client.get(f"/documents/{doc_id}", headers=h2)
    assert r.status_code == 404
