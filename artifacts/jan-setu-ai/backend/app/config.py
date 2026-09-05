from dataclasses import dataclass
from pathlib import Path
import os


ARTIFACT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    app_name: str = "JanSetu AI API"
    environment: str = os.getenv("APP_ENV", "development")
    host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    port: int = int(os.getenv("BACKEND_PORT", "8000"))
    database_path: Path = Path(
        os.getenv(
            "DATABASE_PATH",
            str(ARTIFACT_ROOT / "data" / "jan-setu-ai.db"),
        )
    )
    ai_provider: str = os.getenv("AI_PROVIDER", "auto")
    llm_api_url: str = os.getenv(
        "LLM_API_URL", "https://api.openai.com/v1/chat/completions"
    )
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    llm_timeout_seconds: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "20"))

    @property
    def active_ai_provider(self) -> str:
        if self.ai_provider == "mock":
            return "rules"
        if self.ai_provider == "llm" or self.llm_api_key:
            return "llm"
        return "rules"


settings = Settings()