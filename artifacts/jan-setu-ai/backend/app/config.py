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
    ai_provider: str = os.getenv("AI_PROVIDER", "mock")


settings = Settings()