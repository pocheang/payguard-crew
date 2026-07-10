import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from app.core.environment import Environment

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")



def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    def __init__(self) -> None:
        self.app_name = os.getenv("APP_NAME", "payguard-crew")

        # 使用环境枚举，提供类型安全
        env_str = os.getenv("APP_ENV", "dev")
        self.app_env = Environment.from_string(env_str)

        self.docs_dir = Path(
            os.getenv("PAYGUARD_DOCS_DIR", str(PROJECT_ROOT / "docs"))
        ).resolve()
        self.db_path = Path(
            os.getenv(
                "SQLITE_DB_PATH",
                os.getenv("PAYGUARD_DB_PATH", str(PROJECT_ROOT / "payguard_crew.db")),
            )
        ).resolve()
        self.rag_top_k = int(os.getenv("RAG_TOP_K", "3"))
        self.llm_timeout_seconds = int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
        self.llm_max_retries = int(os.getenv("LLM_MAX_RETRIES", "2"))

        self.llm_provider = os.getenv("LLM_PROVIDER", "deepseek").strip().lower()
        self.enable_crewai = _env_flag("ENABLE_CREWAI", default=False)

        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.openai_base_url = os.getenv("OPENAI_BASE_URL")

        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.deepseek_base_url = os.getenv(
            "DEEPSEEK_BASE_URL", "https://api.deepseek.com"
        )

        self.ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5")
        self.ollama_base_url = os.getenv(
            "OLLAMA_BASE_URL", "http://localhost:11434/v1"
        )

        # 启动时验证配置
        self._validate()
        self._validate_production()

    @property
    def active_api_key(self) -> str | None:
        if self.llm_provider == "openai":
            return self.openai_api_key
        if self.llm_provider == "deepseek":
            return self.deepseek_api_key
        if self.llm_provider == "ollama":
            return "ollama"
        return None

    @property
    def active_model(self) -> str | None:
        if self.llm_provider == "openai":
            return self.openai_model
        if self.llm_provider == "deepseek":
            return self.deepseek_model
        if self.llm_provider == "ollama":
            return self.ollama_model
        return None

    @property
    def active_base_url(self) -> str | None:
        if self.llm_provider == "openai":
            return self.openai_base_url
        if self.llm_provider == "deepseek":
            return self.deepseek_base_url
        if self.llm_provider == "ollama":
            return self.ollama_base_url
        return None

    @property
    def llm_enabled(self) -> bool:
        if self.llm_provider == "disabled":
            return False
        if self.llm_provider == "ollama":
            return bool(self.active_model and self.active_base_url)
        return bool(self.active_api_key and self.active_model)

    @property
    def crewai_model_candidates(self) -> list[str]:
        model = self.active_model
        if not model:
            return []
        if self.llm_provider == "openai":
            return [f"openai/{model}", model]
        if self.llm_provider == "deepseek":
            return [f"deepseek/{model}", f"openai/{model}", model]
        if self.llm_provider == "ollama":
            return [f"ollama/{model}", model]
        return [model]

    def openai_client_kwargs(self) -> dict:
        kwargs = {
            "api_key": self.active_api_key,
            "timeout": self.llm_timeout_seconds,
            "max_retries": self.llm_max_retries,
        }
        if self.active_base_url:
            kwargs["base_url"] = self.active_base_url
        return kwargs

    def _validate(self) -> None:
        """启动时验证配置"""
        # 验证知识库目录
        if not self.docs_dir.exists():
            raise ValueError(
                f"知识库目录不存在: {self.docs_dir}\n"
                f"请设置环境变量 PAYGUARD_DOCS_DIR 或创建 docs/ 目录"
            )

        # 🔒 安全检查：验证路径在项目目录内（防止路径遍历）
        try:
            self.docs_dir.relative_to(PROJECT_ROOT)
        except ValueError:
            raise ValueError(
                f"安全错误：docs_dir 必须在项目根目录内\n"
                f"docs_dir: {self.docs_dir}\n"
                f"PROJECT_ROOT: {PROJECT_ROOT}"
            )

        try:
            self.db_path.relative_to(PROJECT_ROOT)
        except ValueError:
            raise ValueError(
                f"安全错误：db_path 必须在项目根目录内\n"
                f"db_path: {self.db_path}\n"
                f"PROJECT_ROOT: {PROJECT_ROOT}"
            )

        # 检查危险路径模式
        dangerous_patterns = ["..", "~", "/etc", "/root", "/sys", "/proc", "/var"]
        docs_str = str(self.docs_dir)
        db_str = str(self.db_path)

        for pattern in dangerous_patterns:
            if pattern in docs_str or pattern in db_str:
                raise ValueError(
                    f"安全错误：路径包含危险模式 '{pattern}'，可能存在安全风险"
                )

        # 验证 RAG top_k
        if self.rag_top_k < 1 or self.rag_top_k > 10:
            raise ValueError(
                f"RAG_TOP_K 必须在 1-10 之间，当前值: {self.rag_top_k}"
            )

        # 验证 CrewAI 配置
        if self.enable_crewai and not self.llm_enabled:
            raise ValueError(
                "启用 CrewAI (ENABLE_CREWAI=true) 需要配置有效的 LLM:\n"
                f"当前 LLM_PROVIDER={self.llm_provider}\n"
                "请配置对应的 API Key 或将 ENABLE_CREWAI 设置为 false"
            )

        # 🔒 安全检查：验证 API Key 不是默认值
        if self.llm_enabled:
            dangerous_keys = [
                "your_key",
                "your-key",
                "REPLACE-WITH-YOUR-ACTUAL",
                "sk-test",
                "sk-demo",
                "test-key"
            ]
            api_key = self.active_api_key or ""
            if any(key in api_key for key in dangerous_keys):
                raise ValueError(
                    "安全错误：检测到使用默认或测试 API Key\n"
                    "请在 .env 文件中配置真实的 API Key"
                )

        # 验证 LLM 超时和重试
        if self.llm_timeout_seconds < 1 or self.llm_timeout_seconds > 300:
            raise ValueError(
                f"LLM_TIMEOUT_SECONDS 必须在 1-300 之间，当前值: {self.llm_timeout_seconds}"
            )

        if self.llm_max_retries < 0 or self.llm_max_retries > 5:
            raise ValueError(
                f"LLM_MAX_RETRIES 必须在 0-5 之间，当前值: {self.llm_max_retries}"
            )

    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.app_env.is_production

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.app_env.is_development

    def _validate_production(self) -> None:
        """生产环境额外验证（增强安全性）"""
        if not self.is_production:
            return

        import warnings

        # 1. 强制要求强密钥
        jwt_secret = os.getenv("JWT_SECRET_KEY", "")
        if len(jwt_secret) < 32:
            raise ValueError(
                f"🔒 生产环境安全错误：JWT_SECRET_KEY 必须至少32字符\n"
                f"当前长度: {len(jwt_secret)}\n"
                f"建议使用: openssl rand -base64 32"
            )

        # 2. 检查默认密钥
        dangerous_secrets = [
            "your-secret-key-change-in-production",
            "change-me",
            "secret",
            "password",
            "admin"
        ]
        if any(secret in jwt_secret.lower() for secret in dangerous_secrets):
            raise ValueError(
                "🔒 生产环境安全错误：检测到使用默认或弱密钥\n"
                "请使用强随机密钥"
            )

        # 3. 推荐使用 PostgreSQL
        if "sqlite" in str(self.db_path).lower():
            warnings.warn(
                "⚠️  生产环境建议：\n"
                "   使用 PostgreSQL 替代 SQLite 以获得更好的性能和并发支持\n"
                "   设置: DATABASE_URL=postgresql://user:pass@localhost/payguard",
                UserWarning
            )

        # 4. 推荐配置 Redis
        if not os.getenv("REDIS_URL"):
            warnings.warn(
                "⚠️  生产环境建议：\n"
                "   配置 Redis 以支持缓存和限流功能\n"
                "   设置: REDIS_URL=redis://localhost:6379/0",
                UserWarning
            )

        # 5. CORS 安全检查
        allowed_origins = os.getenv("CORS_ORIGINS", "")
        if "*" in allowed_origins:
            raise ValueError(
                "🔒 生产环境安全错误：CORS_ORIGINS 不能使用通配符 *\n"
                "请明确指定允许的域名，例如: https://yourdomain.com"
            )

        if "http://" in allowed_origins and "localhost" not in allowed_origins:
            warnings.warn(
                "⚠️  生产环境安全建议：检测到 HTTP 协议\n"
                "   建议配置 SSL 证书并使用 HTTPS",
                UserWarning
            )

        # 6. API Keys 检查
        api_keys = os.getenv("API_KEYS", "")
        if not api_keys or len(api_keys.split(",")) < 1:
            warnings.warn(
                "⚠️  生产环境建议：配置 API_KEYS 以启用API认证",
                UserWarning
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()
