from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    # 使用项目内的测试目录而不是系统临时目录
    test_db_dir = Path(__file__).parent / "test_data"
    test_db_dir.mkdir(parents=True, exist_ok=True)
    test_db_path = test_db_dir / "payguard-test.db"

    monkeypatch.setenv("SQLITE_DB_PATH", str(test_db_path))
    monkeypatch.setenv(
        "PAYGUARD_DOCS_DIR",
        str((Path(__file__).resolve().parent.parent / "docs").resolve()),
    )
    monkeypatch.setenv("LLM_PROVIDER", "disabled")
    monkeypatch.setenv("ENABLE_CREWAI", "false")
    get_settings.cache_clear()

    with TestClient(app) as test_client:
        yield test_client

    get_settings.cache_clear()
    # 不删除数据库文件，让 .gitignore 忽略 test_data 目录
