import pytest

pytestmark = pytest.mark.asyncio


async def test_register(client):
    r = await client.post("/auth/register", json={
        "email": "new@example.com", "password": "pass12345", "full_name": "New User"
    })
    assert r.status_code == 201
    assert r.json()["email"] == "new@example.com"


async def test_register_duplicate(client):
    body = {"email": "dup@example.com", "password": "pass12345", "full_name": "Dup"}
    await client.post("/auth/register", json=body)
    r = await client.post("/auth/register", json=body)
    assert r.status_code == 409


async def test_register_invalid_email(client):
    r = await client.post("/auth/register", json={
        "email": "notanemail", "password": "pass12345", "full_name": "Bad"
    })
    assert r.status_code == 422


async def test_login_success(client, auth):
    assert "Authorization" in auth


async def test_login_wrong_password(client):
    await client.post("/auth/register", json={
        "email": "u@example.com", "password": "pass12345", "full_name": "U"
    })
    r = await client.post("/auth/login", json={"email": "u@example.com", "password": "wrong"})
    assert r.status_code == 401


async def test_login_unknown_user(client):
    r = await client.post("/auth/login", json={"email": "no@example.com", "password": "pass12345"})
    assert r.status_code == 401


async def test_protected_no_token(client):
    r = await client.get("/documents/")
    assert r.status_code in (401, 403)


async def test_protected_bad_token(client):
    r = await client.get("/documents/", headers={"Authorization": "Bearer bad"})
    assert r.status_code == 401


async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
