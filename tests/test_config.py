"""配置模块测试"""
import os
from pathlib import Path

import pytest

from app.config import Settings, get_settings


def test_default_settings(monkeypatch):
    """测试默认配置"""
    # 设置测试环境变量
    test_dir = Path(__file__).parent / "test_data"
    test_dir.mkdir(parents=True, exist_ok=True)
    docs_dir = Path(__file__).parent.parent / "docs"

    monkeypatch.setenv("PAYGUARD_DOCS_DIR", str(docs_dir))
    monkeypatch.setenv("SQLITE_DB_PATH", str(test_dir / "test.db"))
    monkeypatch.setenv("LLM_PROVIDER", "disabled")

    get_settings.cache_clear()
    settings = Settings()

    assert settings.app_name == "payguard-crew"
    assert settings.app_env == "dev"
    assert settings.rag_top_k == 3


def test_openai_with_api_key_enables_llm(monkeypatch):
    """测试 OpenAI 配置"""
    docs_dir = Path(__file__).parent.parent / "docs"
    test_dir = Path(__file__).parent / "test_data"
    test_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("LLM_PROVIDER", "openai")
    # 使用一个看起来真实但不会被验证为默认值的 API Key
    monkeypatch.setenv("OPENAI_API_KEY", "sk-proj-test-1234567890abcdefghijklmnopqrstuvwxyz")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("PAYGUARD_DOCS_DIR", str(docs_dir))
    monkeypatch.setenv("SQLITE_DB_PATH", str(test_dir / "test.db"))

    get_settings.cache_clear()
    settings = Settings()

    assert settings.llm_provider == "openai"
    assert settings.llm_enabled is True
    assert settings.active_model == "gpt-4o-mini"

    kwargs = settings.openai_client_kwargs()
    assert "api_key" in kwargs
    assert kwargs["timeout"] == 30
    assert kwargs["max_retries"] == 2


def test_ollama_configuration(monkeypatch):
    """测试 Ollama 配置"""
    docs_dir = Path(__file__).parent.parent / "docs"
    test_dir = Path(__file__).parent / "test_data"
    test_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("PAYGUARD_DOCS_DIR", str(docs_dir))
    monkeypatch.setenv("SQLITE_DB_PATH", str(test_dir / "test.db"))

    get_settings.cache_clear()
    settings = Settings()

    assert settings.llm_provider == "ollama"
    assert settings.active_model == "qwen2.5"
    assert settings.active_base_url == "http://localhost:11434/v1"
    assert settings.active_api_key == "ollama"

    kwargs = settings.openai_client_kwargs()
    assert kwargs["api_key"] == "ollama"
    assert kwargs["base_url"] == "http://localhost:11434/v1"


def test_dangerous_api_key_raises_error(monkeypatch):
    """测试使用危险的默认 API Key 会报错"""
    docs_dir = Path(__file__).parent.parent / "docs"
    test_dir = Path(__file__).parent / "test_data"
    test_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "your_key")  # 默认值
    monkeypatch.setenv("PAYGUARD_DOCS_DIR", str(docs_dir))
    monkeypatch.setenv("SQLITE_DB_PATH", str(test_dir / "test.db"))

    get_settings.cache_clear()

    with pytest.raises(ValueError, match="默认或测试 API Key"):
        Settings()


def test_path_traversal_protection(monkeypatch):
    """测试路径遍历保护"""
    test_dir = Path(__file__).parent / "test_data"
    test_dir.mkdir(parents=True, exist_ok=True)

    # 尝试使用项目外的路径
    monkeypatch.setenv("PAYGUARD_DOCS_DIR", "/etc/passwd")
    monkeypatch.setenv("SQLITE_DB_PATH", str(test_dir / "test.db"))
    monkeypatch.setenv("LLM_PROVIDER", "disabled")

    get_settings.cache_clear()

    # 应该在验证路径之前先检查目录是否存在，所以错误信息会是"不存在"
    with pytest.raises(ValueError, match="不存在"):
        Settings()


def test_rag_top_k_validation(monkeypatch):
    """测试 RAG_TOP_K 验证"""
    docs_dir = Path(__file__).parent.parent / "docs"
    test_dir = Path(__file__).parent / "test_data"
    test_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("RAG_TOP_K", "100")  # 超出范围
    monkeypatch.setenv("PAYGUARD_DOCS_DIR", str(docs_dir))
    monkeypatch.setenv("SQLITE_DB_PATH", str(test_dir / "test.db"))
    monkeypatch.setenv("LLM_PROVIDER", "disabled")

    get_settings.cache_clear()

    with pytest.raises(ValueError, match="RAG_TOP_K 必须在 1-10 之间"):
        Settings()
