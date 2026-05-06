import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routes import auth, documents, media, chat


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="DocQA API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(media.router)
app.include_router(chat.router)


@app.get("/health")
def health():
    return {"status": "ok"}
