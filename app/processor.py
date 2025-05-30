from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal, Optional
import httpx, os, logging
from .config import load_settings
from .utils import init_cache, download_audio, convert_to_wav, cleanup_file

settings = load_settings()
logger = logging.getLogger("processor.router")

router = APIRouter()

class DownloadRequest(BaseModel):
    videoUrl: str
    cachePolicy: Literal["if-missing","always"] = "if-missing"

class DownloadResponse(BaseModel):
    status: str
    message: str
    audioPath: Optional[str] = None
    srt: Optional[str] = None

@router.post("/download-preprocess", response_model=DownloadResponse)
async def download_and_preprocess(req: DownloadRequest):
    try:
        # 1) 캐시 초기화
        cache = init_cache(settings.TMP_ROOT, req.cachePolicy)
        # 2) 다운로드
        mp4 = download_audio(req.videoUrl, cache, req.cachePolicy)
        # 3) 변환
        wav = os.path.join(cache, "audio.wav")
        convert_to_wav(mp4, wav)
        # 4) MP4 정리
        cleanup_file(mp4)
        # 5) Whisper 연동
        logger.info("Sending to Whisper at %s", settings.WHISPER_URL)
        async with httpx.AsyncClient(timeout=120) as client:
            with open(wav,"rb") as f:
                resp = await client.post(settings.WHISPER_URL,
                                         files={"file":f})
            resp.raise_for_status()
            data = resp.json()
        srt = data.get("srt") or data.get("text")
        # 6) 응답
        return DownloadResponse(
            status="success",
            message="Done",
            audioPath=wav,
            srt=srt
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error pipeline: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
