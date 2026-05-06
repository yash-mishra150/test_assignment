"""Unit tests for rag.py — real implementations with mocked Ollama/FAISS."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.documents import Document

import app.rag as _rag

_real_get_embeddings = _rag.get_embeddings
_real_get_llm = _rag.get_llm
_real_stream_answer = _rag.stream_answer
_real_summarize = _rag.summarize


def test_get_embeddings_singleton(monkeypatch):
    monkeypatch.setattr(_rag, "_embeddings", None)
    with patch("app.rag.OllamaEmbeddings") as mock_cls:
        mock_cls.return_value = MagicMock()
        e1 = _real_get_embeddings()
        e2 = _real_get_embeddings()
        assert e1 is e2
        mock_cls.assert_called_once()


def test_get_llm_singleton(monkeypatch):
    monkeypatch.setattr(_rag, "_llm", None)
    with patch("app.rag.ChatOllama") as mock_cls:
        mock_cls.return_value = MagicMock()
        l1 = _real_get_llm()
        l2 = _real_get_llm()
        assert l1 is l2
        mock_cls.assert_called_once()


@pytest.mark.asyncio
async def test_stream_answer(monkeypatch):
    mock_chunk1 = MagicMock(); mock_chunk1.content = "Hello "
    mock_chunk2 = MagicMock(); mock_chunk2.content = "world"

    async def fake_astream(_prompt):
        for c in [mock_chunk1, mock_chunk2]:
            yield c

    mock_llm = MagicMock()
    mock_llm.astream = fake_astream
    monkeypatch.setattr(_rag, "get_llm", lambda: mock_llm)

    docs = [Document(page_content="context", metadata={"source": "test.pdf"})]
    tokens = [t async for t in _real_stream_answer("question?", docs)]
    assert "Hello " in tokens
    assert "world" in tokens


@pytest.mark.asyncio
async def test_summarize(monkeypatch):
    mock_result = MagicMock(); mock_result.content = "  A summary.  "
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(return_value=mock_result)
    monkeypatch.setattr(_rag, "get_llm", lambda: mock_llm)

    result = await _real_summarize("Some long text")
    assert result == "A summary."


@pytest.mark.asyncio
async def test_summarize_truncates_long_text(monkeypatch):
    mock_result = MagicMock(); mock_result.content = "Summary"
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(return_value=mock_result)
    monkeypatch.setattr(_rag, "get_llm", lambda: mock_llm)

    await _real_summarize("x" * 5000)
    call_arg = mock_llm.ainvoke.call_args[0][0]
    assert len(call_arg) < 4000


@pytest.mark.asyncio
async def test_stream_answer_skips_empty_content(monkeypatch):
    mock_c1 = MagicMock(); mock_c1.content = ""
    mock_c2 = MagicMock(); mock_c2.content = "real"

    async def fake_astream(_prompt):
        for c in [mock_c1, mock_c2]:
            yield c

    mock_llm = MagicMock()
    mock_llm.astream = fake_astream
    monkeypatch.setattr(_rag, "get_llm", lambda: mock_llm)

    docs = [Document(page_content="ctx", metadata={})]
    tokens = [t async for t in _real_stream_answer("q", docs)]
    assert tokens == ["real"]
