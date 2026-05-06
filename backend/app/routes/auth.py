from datetime import datetime, timezone
from uuid import uuid4

import aiosqlite
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.security import create_token, decode_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])
bearer = HTTPBearer()


class RegisterBody(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class LoginBody(BaseModel):
    email: EmailStr
    password: str


async def current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    uid = decode_token(creds.credentials)
    if not uid:
        raise HTTPException(401, "Invalid token")
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE id=?", (uid,)) as c:
            row = await c.fetchone()
    if not row:
        raise HTTPException(401, "User not found")
    return dict(row)


@router.post("/register", status_code=201)
async def register(body: RegisterBody):
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id FROM users WHERE email=?", (body.email,)) as c:
            if await c.fetchone():
                raise HTTPException(409, "Email already registered")
        uid = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        await db.execute(
            "INSERT INTO users VALUES (?,?,?,?,?)",
            (uid, body.email, body.full_name, hash_password(body.password), now),
        )
        await db.commit()
    return {"id": uid, "email": body.email, "full_name": body.full_name}


@router.post("/login")
async def login(body: LoginBody):
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE email=?", (body.email,)) as c:
            row = await c.fetchone()
    if not row or not verify_password(body.password, row["hashed_password"]):
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": create_token(row["id"]), "token_type": "bearer"}
