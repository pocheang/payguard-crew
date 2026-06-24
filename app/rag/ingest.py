from __future__ import annotations

from pathlib import Path

from app.config import get_settings
from app.rag.vector_store import ChromaVectorStore, VectorChunk


def _chunk_markdown(source: str, text: str) -> list[VectorChunk]:
    chunks: list[VectorChunk] = []
    current_heading = "Document"
    paragraph_buffer: list[str] = []
    chunk_index = 0

    def flush_paragraphs() -> None:
        nonlocal chunk_index
        paragraph_text = "\n\n".join(part.strip() for part in paragraph_buffer if part.strip()).strip()
        paragraph_buffer.clear()
        if not paragraph_text:
            return
        content = f"{current_heading}\n\n{paragraph_text}" if current_heading else paragraph_text
        chunks.append(
            VectorChunk(
                chunk_id=f"{source}:{chunk_index}",
                source=source,
                content=content,
                heading=current_heading,
            )
        )
        chunk_index += 1

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("#"):
            flush_paragraphs()
            current_heading = line.lstrip("#").strip() or current_heading
            continue
        if not line:
            flush_paragraphs()
            continue
        paragraph_buffer.append(line)

    flush_paragraphs()
    return chunks


def load_markdown_chunks(docs_dir: str | Path | None = None) -> list[VectorChunk]:
    settings = get_settings()
    base_docs_dir = Path(docs_dir or settings.docs_dir)
    chunks: list[VectorChunk] = []

    for path in sorted(base_docs_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        chunks.extend(_chunk_markdown(path.name, text))

    return chunks


def ingest_markdown_docs(
    docs_dir: str | Path | None = None,
    persist_dir: str | Path | None = None,
    collection_name: str = "payguard_docs",
) -> dict[str, int | str]:
    chunks = load_markdown_chunks(docs_dir=docs_dir)
    store = ChromaVectorStore(
        persist_dir=persist_dir,
        collection_name=collection_name,
    )
    ingested_chunks = store.upsert_chunks(chunks)
    return {
        "collection_name": collection_name,
        "chunk_count": ingested_chunks,
        "document_count": len({chunk.source for chunk in chunks}),
        "persist_dir": str(store.persist_dir),
    }
