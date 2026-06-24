from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.config import get_settings
from app.schemas.audit import EvidenceItem


TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]{1}")


class LocalHashEmbeddingFunction:
    def __init__(self, dimension: int = 256):
        self.dimension = dimension

    def __call__(self, input: list[str]) -> list[list[float]]:
        return [self.embed_text(text) for text in input]

    @staticmethod
    def name() -> str:
        return "payguard_local_hash"

    def get_config(self) -> dict[str, Any]:
        return {"name": self.name(), "dimension": self.dimension}

    @staticmethod
    def is_legacy() -> bool:
        return False

    @staticmethod
    def default_space() -> str:
        return "l2"

    @staticmethod
    def supported_spaces() -> list[str]:
        return ["cosine", "l2", "ip"]

    @staticmethod
    def build_from_config(config: dict[str, Any]) -> "LocalHashEmbeddingFunction":
        return LocalHashEmbeddingFunction(dimension=int(config.get("dimension", 256)))

    def _index_for_token(self, token: str) -> int:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        return int.from_bytes(digest[:4], "big") % self.dimension

    def embed_text(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        tokens = TOKEN_PATTERN.findall(text.lower())
        if not tokens:
            return vector

        for token in tokens:
            vector[self._index_for_token(token)] += 1.0

        norm = sum(value * value for value in vector) ** 0.5
        if norm == 0:
            return vector
        return [value / norm for value in vector]

    def embed_query(self, input: list[str]) -> list[list[float]]:
        """ChromaDB requires this method for query embedding"""
        return [self.embed_text(text) for text in input]


@dataclass
class VectorChunk:
    chunk_id: str
    source: str
    content: str
    heading: str | None = None

    @property
    def metadata(self) -> dict[str, str]:
        metadata = {"source": self.source}
        if self.heading:
            metadata["heading"] = self.heading
        return metadata


class ChromaVectorStore:
    def __init__(
        self,
        persist_dir: str | Path | None = None,
        collection_name: str = "payguard_docs",
        embedding_function: LocalHashEmbeddingFunction | None = None,
    ) -> None:
        settings = get_settings()
        self.persist_dir = Path(persist_dir or (settings.docs_dir.parent / ".chroma")).resolve()
        self.collection_name = collection_name
        self.embedding_function = embedding_function or LocalHashEmbeddingFunction()
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError("chromadb is not installed") from exc

        self._client = chromadb.PersistentClient(path=str(self.persist_dir))
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
            metadata={"description": "PayGuard Crew markdown knowledge base"},
        )

    def count(self) -> int:
        return self._collection.count()

    def upsert_chunks(self, chunks: list[VectorChunk]) -> int:
        if not chunks:
            return 0

        self._collection.upsert(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.content for chunk in chunks],
            metadatas=[chunk.metadata for chunk in chunks],
        )
        return len(chunks)

    def query(self, query: str, top_k: int = 3) -> list[EvidenceItem]:
        if self.count() == 0:
            return []

        result = self._collection.query(query_texts=[query], n_results=top_k)
        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]

        evidence: list[EvidenceItem] = []
        for document, metadata in zip(documents, metadatas):
            if not document:
                continue
            source = (metadata or {}).get("source")
            if not source:
                continue
            evidence.append(EvidenceItem(source=source, content=document))
        return evidence
