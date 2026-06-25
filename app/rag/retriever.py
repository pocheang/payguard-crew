from __future__ import annotations

from pathlib import Path

from app.config import get_settings
from app.rag.simple_retriever import SimpleMarkdownRetriever
from app.rag.vector_store import ChromaVectorStore
from app.schemas.audit import EvidenceItem


class AuditEvidenceRetriever:
    def __init__(
        self,
        docs_dir: str | Path | None = None,
        persist_dir: str | Path | None = None,
        collection_name: str = "payguard_docs",
    ) -> None:
        settings = get_settings()
        self.docs_dir = Path(docs_dir or settings.docs_dir)
        self.simple_retriever = SimpleMarkdownRetriever(docs_dir=self.docs_dir)
        self.vector_store: ChromaVectorStore | None = None

        try:
            self.vector_store = ChromaVectorStore(
                persist_dir=persist_dir,
                collection_name=collection_name,
            )
        except Exception:
            self.vector_store = None

    def retrieve(self, query: str, top_k: int = 3) -> list[EvidenceItem]:
        if self.vector_store is not None:
            try:
                evidence = self.vector_store.query(query=query, top_k=top_k)
                if evidence:
                    return evidence
            except Exception:
        # 空实现
        return self.simple_retriever.retrieve(query=query, top_k=top_k)
