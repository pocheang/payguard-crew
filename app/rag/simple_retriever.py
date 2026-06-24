from pathlib import Path

from app.config import get_settings
from app.schemas.audit import EvidenceItem


class SimpleMarkdownRetriever:
    """
    Minimal keyword-based retriever for demo stage.

    Codex next step:
    - Replace or extend this with ChromaDB vector search.
    - Keep the return format compatible with EvidenceItem.
    """

    def __init__(self, docs_dir: str | Path | None = None):
        base_docs_dir = docs_dir or get_settings().docs_dir
        self.docs_dir = Path(base_docs_dir)

    def retrieve(self, query: str, top_k: int = 3) -> list[EvidenceItem]:
        if not self.docs_dir.exists():
            return []

        query_terms = {term.lower() for term in query.split() if len(term) >= 2}
        scored_chunks: list[tuple[int, str, str]] = []

        for path in self.docs_dir.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
            for chunk in chunks:
                chunk_lower = chunk.lower()
                score = sum(1 for term in query_terms if term in chunk_lower)
                for kw in [
                    "新账户",
                    "大额",
                    "高频",
                    "KYC",
                    "AML",
                    "IP",
                    "设备",
                    "人工复核",
                    "黑名单",
                ]:
                    if kw.lower() in chunk_lower and kw.lower() in query.lower():
                        score += 2
                if score > 0:
                    scored_chunks.append((score, path.name, chunk))

        scored_chunks.sort(key=lambda item: item[0], reverse=True)
        return [
            EvidenceItem(source=source, content=content)
            for _, source, content in scored_chunks[:top_k]
        ]
