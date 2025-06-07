import os
#from pydantic import BaseSettings
#class Settings(BaseSettings):

#현재 env는 무시하고 config.py에서 설정된값만 사용합니다.
class Settings:
    PORT: int = 8000
    DEBUG: bool = False
    TMP_ROOT: str = "/tmp/download_preprocess"
    WHISPER_URL: str = "http://54.180.24.69:8002/internal/transcribe"

#   class Config:
#       env_file = ".env"
#       env_file_encoding = "utf-8"

def load_settings() -> Settings:
    return Settings()
