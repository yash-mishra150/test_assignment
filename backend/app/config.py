from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ollama_url: str = "http://localhost:11434"
    llm_model: str = "qwen3.5:9b"
    embed_model: str = "all-minilm"
    data_dir: Path = Path("./data")

    jwt_secret: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    @property
    def db_path(self) -> Path:
        return self.data_dir / "docqa.db"

    @property
    def faiss_path(self) -> Path:
        return self.data_dir / "faiss_store"

    @property
    def media_dir(self) -> Path:
        return self.data_dir / "media"


settings = Settings()
