from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    finnhub_api_key: str

    model_config = {
        "env_file": str(Path(__file__).parent / ".env")
    }
