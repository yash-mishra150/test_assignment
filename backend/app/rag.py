"""
RAG layer — LangChain handles embeddings, vector store, and LLM.
One global FAISS store persisted to disk.
"""
from __future__ import annotations
from typing import AsyncGenerator, List
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.config import settings

_store: FAISS | None = None
_embeddings: OllamaEmbeddings | None = None
_llm: ChatOllama | None = None

SYSTEM = (
    "You are a helpful assistant. Answer the question using only the provided context. "
    "If the context doesn't have enough information, say so clearly."
)


def get_embeddings() -> OllamaEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = OllamaEmbeddings(model=settings.embed_model, base_url=settings.ollama_url)
    return _embeddings


def get_llm() -> ChatOllama:
    global _llm
    if _llm is None:
        _llm = ChatOllama(model=settings.llm_model, base_url=settings.ollama_url)
    return _llm


def get_store() -> FAISS | None:
    global _store
    if _store is None and settings.faiss_path.exists():
        _store = FAISS.load_local(
            str(settings.faiss_path), get_embeddings(), allow_dangerous_deserialization=True
        )
    return _store


def add_documents(docs: List[Document]):
    global _store
    settings.faiss_path.parent.mkdir(parents=True, exist_ok=True)
    if _store is None:
        _store = FAISS.from_documents(docs, get_embeddings())
    else:
        _store.add_documents(docs)
    _store.save_local(str(settings.faiss_path))


def search(query: str, doc_ids: List[str] | None = None, user_id: str | None = None, k: int = 5) -> List[Document]:
    store = get_store()
    if not store:
        return []
    results = store.similarity_search(query, k=k * 3)
    if user_id:
        results = [d for d in results if d.metadata.get("user_id") == user_id]
    if doc_ids:
        results = [d for d in results if d.metadata.get("doc_id") in doc_ids]
    return results[:k]


async def stream_answer(query: str, context_docs: List[Document]) -> AsyncGenerator[str, None]:
    context = "\n\n---\n\n".join(
        f"[{d.metadata.get('source', 'doc')}]\n{d.page_content}" for d in context_docs
    )
    prompt = f"{SYSTEM}\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:"
    async for chunk in get_llm().astream(prompt):
        if chunk.content:
            yield chunk.content


async def summarize(text: str) -> str:
    truncated = text[:3000]
    result = await get_llm().ainvoke(f"Summarize in 3-4 sentences:\n\n{truncated}")
    return result.content.strip()
