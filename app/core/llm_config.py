"""
LLM配置模块

从config.py中提取，单独管理LLM相关配置
"""
import os
from typing import Any


class LLMConfig:
    """LLM配置类"""

    def __init__(self):
        # LLM提供商
        self.llm_provider = os.getenv("LLM_PROVIDER", "disabled").lower()
        self.llm_enabled = self.llm_provider != "disabled"

        # OpenAI配置
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.openai_base_url = os.getenv("OPENAI_BASE_URL") or None

        # DeepSeek配置
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

        # Ollama配置
        self.ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

        # 超时和重试
        self.llm_timeout_seconds = int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
        self.llm_max_retries = int(os.getenv("LLM_MAX_RETRIES", "2"))

        # CrewAI配置
        self.enable_crewai = os.getenv("ENABLE_CREWAI", "false").lower() == "true"

        # 自动选择活跃的API密钥和模型
        self._select_active_llm()

    def _select_active_llm(self):
        """根据provider选择活跃的LLM配置"""
        if self.llm_provider == "openai" and self.openai_api_key:
            self.active_api_key = self.openai_api_key
            self.active_model = self.openai_model
            self.active_base_url = self.openai_base_url
        elif self.llm_provider == "deepseek" and self.deepseek_api_key:
            self.active_api_key = self.deepseek_api_key
            self.active_model = self.deepseek_model
            self.active_base_url = self.deepseek_base_url
        elif self.llm_provider == "ollama":
            self.active_api_key = "ollama"
            self.active_model = self.ollama_model
            self.active_base_url = self.ollama_base_url
        else:
            self.active_api_key = None
            self.active_model = None
            self.active_base_url = None

    @property
    def crewai_model_priority(self) -> list[str]:
        """CrewAI模型优先级列表"""
        if self.llm_provider == "deepseek":
            return [self.deepseek_model]
        elif self.llm_provider == "ollama":
            return [self.ollama_model]
        elif self.llm_provider == "openai":
            return [self.openai_model]
        return []

    def openai_client_kwargs(self) -> dict[str, Any]:
        """OpenAI客户端参数"""
        kwargs = {"api_key": self.active_api_key or ""}
        if self.active_base_url:
            kwargs["base_url"] = self.active_base_url
        return kwargs

    def validate(self, app_env: str) -> None:
        """验证LLM配置"""
        # 验证CrewAI配置
        if self.enable_crewai and not self.llm_enabled:
            raise ValueError(
                f"ENABLE_CREWAI=true requires valid LLM. "
                f"Current LLM_PROVIDER={self.llm_provider}"
            )

        # 安全检查：验证API Key不是默认值
        if self.llm_enabled:
            dangerous_keys = [
                "your_key", "your-key", "REPLACE-WITH-YOUR-ACTUAL",
                "sk-test", "sk-demo", "test-key"
            ]
            api_key = self.active_api_key or ""
            if any(key in api_key for key in dangerous_keys):
                raise ValueError(
                    "Security Error: Using default/test API Key"
                )

        # 验证超时和重试
        if not (1 <= self.llm_timeout_seconds <= 300):
            raise ValueError(
                f"LLM_TIMEOUT_SECONDS must be 1-300, got {self.llm_timeout_seconds}"
            )

        if not (0 <= self.llm_max_retries <= 5):
            raise ValueError(
                f"LLM_MAX_RETRIES must be 0-5, got {self.llm_max_retries}"
            )
