from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.rag.ingest import ingest_markdown_docs


if __name__ == "__main__":
    result = ingest_markdown_docs()
    print(
        "Indexed {chunk_count} chunks from {document_count} docs into {collection_name} at {persist_dir}".format(
            **result
        )
    )
