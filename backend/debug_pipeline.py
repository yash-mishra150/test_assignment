"""
Run this to benchmark each step independently:
  python debug_pipeline.py path/to/file.pdf
"""
import sys, time, asyncio

def check(label, fn):
    t = time.perf_counter()
    result = fn()
    print(f"  ✓ {label}: {time.perf_counter()-t:.2f}s  →  {repr(result)[:80]}")
    return result

async def acheck(label, coro):
    t = time.perf_counter()
    result = await coro
    print(f"  ✓ {label}: {time.perf_counter()-t:.2f}s  →  {repr(result)[:80]}")
    return result

async def main(pdf_path: str):
    import fitz
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_ollama import OllamaEmbeddings, ChatOllama
    from langchain_community.vectorstores import FAISS
    from app.config import settings

    print("\n=== Step 1: PDF extraction ===")
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = check("extract text", lambda: "\n\n".join(p.get_text() for p in doc))
    doc.close()
    print(f"  chars: {len(text)}, pages: {doc.page_count}")

    print("\n=== Step 2: Chunking ===")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = check("split", lambda: splitter.create_documents([text]))
    print(f"  chunks: {len(chunks)}")

    print("\n=== Step 3: Embedding (Ollama all-minilm) ===")
    embeddings = OllamaEmbeddings(model=settings.embed_model, base_url=settings.ollama_url)
    texts = [c.page_content for c in chunks]
    await acheck(f"embed {len(texts)} chunks", embeddings.aembed_documents(texts))

    print("\n=== Step 4: FAISS store ===")
    check("build FAISS index", lambda: FAISS.from_documents(chunks[:3], embeddings))

    print("\n=== Step 5: LLM summary (qwen3.5:9b) ===")
    llm = ChatOllama(model=settings.llm_model, base_url=settings.ollama_url)
    await acheck("summarize (first 1000 chars)", llm.ainvoke(f"Summarize in 2 sentences:\n\n{text[:1000]}"))

    print("\n=== All steps done ===")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if not path:
        print("Usage: python debug_pipeline.py path/to/file.pdf")
        sys.exit(1)
    asyncio.run(main(path))
