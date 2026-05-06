import json
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app.rag import search, stream_answer
from app.routes.auth import current_user

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    query: str
    doc_ids: Optional[List[str]] = None


def _strip_thinking(token: str, state: dict) -> str:
    """Drop <think>...</think> blocks that qwen3.5 emits before the real answer."""
    buf = state.get("buf", "") + token
    output = ""

    while buf:
        if state.get("in_think"):
            end = buf.find("</think>")
            if end != -1:
                state["in_think"] = False
                buf = buf[end + len("</think>"):]
            else:
                buf = ""
        else:
            start = buf.find("<think>")
            if start != -1:
                output += buf[:start]
                state["in_think"] = True
                buf = buf[start + len("<think>"):]
            else:
                output += buf
                buf = ""

    state["buf"] = ""
    return output


@router.post("/stream")
async def chat_stream(body: ChatRequest, user: dict = Depends(current_user)):
    async def generate():
        docs = search(body.query, doc_ids=body.doc_ids, user_id=user["id"])

        if not docs:
            yield {"event": "token", "data": "No relevant documents found. Please upload some files first."}
            yield {"event": "done", "data": ""}
            return

        think_state: dict = {}
        async for token in stream_answer(body.query, docs):
            clean = _strip_thinking(token, think_state)
            if clean:
                yield {"event": "token", "data": clean}

        sources = []
        seen = set()
        for d in docs:
            m = d.metadata
            key = (m.get("doc_id"), m.get("start_sec"))
            if key not in seen:
                seen.add(key)
                sources.append({
                    "doc_id": m.get("doc_id"),
                    "source": m.get("source"),
                    "start_sec": m.get("start_sec"),
                    "end_sec": m.get("end_sec"),
                })

        yield {"event": "sources", "data": json.dumps(sources)}
        yield {"event": "done", "data": ""}

    return EventSourceResponse(generate())
