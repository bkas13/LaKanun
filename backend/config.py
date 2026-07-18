"""Backend configuration — environment-based settings."""

import os
from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Paths ──────────────────────────────────────────────────────────
    project_root: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = Path(__file__).resolve().parent.parent / "data"
    processed_data_dir: Path = Path(__file__).resolve().parent.parent / "data" / "processed"
    db_path: Path = Path(__file__).resolve().parent.parent / "data" / "kanun.db"

    # ── Auth ───────────────────────────────────────────────────────────
    secret_key: str = "dev-secret-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # ── API ────────────────────────────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_v1_prefix: str = "/api/v1"
    allowed_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3030", "http://127.0.0.1:3030"]
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    # ── Embeddings (for law search) ───────────────────────────────────
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    collection_prefix: str = "law"

    # ── Supported ──────────────────────────────────────────────────────
    supported_countries: List[str] = ["nepal", "india"]
    supported_languages: List[str] = ["en", "ne", "hi"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def database_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.db_path}"


settings = Settings()
