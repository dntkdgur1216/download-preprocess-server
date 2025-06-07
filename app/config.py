import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    PORT: int = 8000
    DEBUG: bool = False
    TMP_ROOT: str = "/tmp/download_preprocess"
    WHISPER_URL: str = "http://54.180.24.69:8002/internal/transcribe"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def load_settings() -> Settings:
    return Settings()
