from fastapi import FastAPI
from app.processor import router
from app.config import load_settings

settings = load_settings()

app = FastAPI(
    title="Download & Preprocess Service",
    description="YouTube→WAV→Whisper 통합 파이프라인"
)
app.include_router(router, prefix="/internal")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(settings.PORT),
        reload=settings.DEBUG
    )
