from app.rag.retriever import AuditEvidenceRetriever
from app.rag.simple_retriever import SimpleMarkdownRetriever



def test_simple_retriever_returns_evidence_items() -> None:
    evidence = SimpleMarkdownRetriever().retrieve("KYC AML IP abnormal", top_k=2)

    assert evidence
    assert len(evidence) <= 2
    assert all(item.source for item in evidence)
    assert all(item.content for item in evidence)



def test_vector_retriever_returns_evidence_items(tmp_path) -> None:
    from app.rag.ingest import ingest_markdown_docs

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "policy.md").write_text(
        "# KYC Policy\n\nKYC incomplete accounts should be reviewed.\n\n# AML Policy\n\nAbnormal IP and high frequency transactions require review.",
        encoding="utf-8",
    )

    persist_dir = tmp_path / "chroma"
    ingest_markdown_docs(docs_dir=docs_dir, persist_dir=persist_dir, collection_name="test_docs")

    evidence = AuditEvidenceRetriever(
        docs_dir=docs_dir,
        persist_dir=persist_dir,
        collection_name="test_docs",
    ).retrieve("KYC abnormal IP high frequency", top_k=2)

    assert evidence
    assert len(evidence) <= 2
    assert all(item.source == "policy.md" for item in evidence)
    assert all(item.content for item in evidence)



def test_vector_retriever_falls_back_to_simple_retriever(tmp_path, monkeypatch) -> None:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "policy.md").write_text(
        "# Manual Review\n\nManual review is required for abnormal device and KYC mismatch.",
        encoding="utf-8",
    )

    retriever = AuditEvidenceRetriever(docs_dir=docs_dir, persist_dir=tmp_path / "chroma")

    class BrokenStore:
        def query(self, query: str, top_k: int = 3):
            raise RuntimeError("broken chroma")

    retriever.vector_store = BrokenStore()

    evidence = retriever.retrieve("abnormal device KYC", top_k=1)

    assert evidence
    assert evidence[0].source == "policy.md"
    assert "KYC" in evidence[0].content
