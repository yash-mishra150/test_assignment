"""Unit tests. Real function refs captured at import time — before autouse patches."""
import io
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document

# Capture real implementations before autouse fixtures patch them
import app.rag as _rag
import app.routes.chat as _chat
import app.routes.documents as _docs_mod

_real_search = _rag.search
_real_add_documents = _rag.add_documents
_real_strip_thinking = _chat._strip_thinking
_real_extract_text = _docs_mod._extract_text


# ─── security ────────────────────────────────────────────────────────────────

def test_hash_and_verify():
    from app.security import hash_password, verify_password
    h = hash_password("mypassword")
    assert verify_password("mypassword", h)
    assert not verify_password("wrong", h)


def test_token_roundtrip():
    from app.security import create_token, decode_token
    assert decode_token(create_token("user123")) == "user123"


def test_invalid_token():
    from app.security import decode_token
    assert decode_token("not.a.real.token") is None


# ─── rag search ──────────────────────────────────────────────────────────────

def test_search_empty_store(monkeypatch):
    monkeypatch.setattr(_rag, "_store", None)
    monkeypatch.setattr(_rag, "get_store", lambda: None)
    assert _real_search("hello") == []


def test_search_filters_by_user(monkeypatch):
    docs = [
        Document(page_content="A", metadata={"doc_id": "1", "user_id": "alice"}),
        Document(page_content="B", metadata={"doc_id": "2", "user_id": "bob"}),
    ]
    mock_store = MagicMock()
    mock_store.similarity_search.return_value = docs
    monkeypatch.setattr(_rag, "get_store", lambda: mock_store)
    results = _real_search("q", user_id="alice")
    assert len(results) == 1
    assert results[0].metadata["user_id"] == "alice"


def test_search_filters_by_doc_id(monkeypatch):
    docs = [
        Document(page_content="A", metadata={"doc_id": "doc1", "user_id": "u1"}),
        Document(page_content="B", metadata={"doc_id": "doc2", "user_id": "u1"}),
    ]
    mock_store = MagicMock()
    mock_store.similarity_search.return_value = docs
    monkeypatch.setattr(_rag, "get_store", lambda: mock_store)
    results = _real_search("q", doc_ids=["doc1"])
    assert len(results) == 1
    assert results[0].metadata["doc_id"] == "doc1"


def test_add_documents_new_store(tmp_path, monkeypatch):
    monkeypatch.setattr(_rag, "_store", None)
    mock_store = MagicMock()
    import app.config as cfg
    monkeypatch.setattr(cfg.settings, "data_dir", tmp_path)

    with patch.object(_rag, "FAISS") as mock_faiss, \
         patch.object(_rag, "get_embeddings", return_value=MagicMock()):
        mock_faiss.from_documents.return_value = mock_store
        mock_store.save_local = MagicMock()
        _real_add_documents([Document(page_content="hi", metadata={})])
        mock_faiss.from_documents.assert_called_once()


# ─── think-tag stripping ──────────────────────────────────────────────────────

def test_strip_no_tags():
    assert _real_strip_thinking("Hello world", {}) == "Hello world"


def test_strip_inline_block():
    result = _real_strip_thinking("<think>hidden</think>visible", {})
    assert "visible" in result
    assert "hidden" not in result


def test_strip_multitoken_block():
    state = {}
    _real_strip_thinking("<think>", state)
    _real_strip_thinking("internal reasoning", state)
    result = _real_strip_thinking("</think>Real answer", state)
    assert "Real answer" in result
    assert "internal" not in result


def test_strip_passthrough():
    state = {}
    out = "".join(_real_strip_thinking(t, state) for t in ["The ", "answer ", "is 42."])
    assert "answer" in out and "42" in out


def test_strip_text_before_think():
    result = _real_strip_thinking("Prefix<think>hidden</think>suffix", {})
    assert "Prefix" in result
    assert "suffix" in result
    assert "hidden" not in result


# ─── pdf extraction ───────────────────────────────────────────────────────────

def test_extract_text(sample_pdf):
    text = _real_extract_text(sample_pdf)
    assert isinstance(text, str) and len(text) > 0


def test_extract_text_blank_page():
    import fitz
    doc = fitz.open()
    doc.new_page()
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    assert _real_extract_text(buf.getvalue()).strip() == ""


# ─── transcription mock ───────────────────────────────────────────────────────

def test_transcribe_returns_segments(tmp_path):
    from app.routes.media import _transcribe
    audio = str(tmp_path / "a.mp3")
    open(audio, "wb").close()
    segs = _transcribe(audio)  # patched by autouse fixture
    assert segs[0]["text"] == "Hello world"
    assert segs[0]["start"] == 0.0
