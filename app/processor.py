from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
# from typing import Literal, Optional
import httpx, os, logging
from .config import load_settings
from .utils import init_cache, download_audio, convert_to_wav, cleanup_file


settings = load_settings()
logger = logging.getLogger("processor.router")

router = APIRouter()

class ProcessAudioRequest(BaseModel):
    videoTitle: str
    videoUrl: HttpUrl

@router.post("/process-audio")
async def download_and_preprocess(req: ProcessAudioRequest):
    try:
        # 1) 캐시 디렉터리 생성: 영상별
        cache_root = os.path.join(settings.TMP_ROOT, req.videoTitle)
        cache_dir = init_cache(cache_root, "if-missing")

        # 2) 오디오 전용 다운로드
        audio_src = download_audio(req.videoUrl, cache_dir, "if-missing")

        # 3) WAV 변환 및 원본 삭제
        wav_path = os.path.join(cache_dir, f"{req.videoTitle}.wav")
        convert_to_wav(audio_src, wav_path)
        cleanup_file(audio_src)

        # 4) Whisper 서버 전송
        logger.info("Sending audio to Whisper at %s", settings.WHISPER_URL)
        async with httpx.AsyncClient(timeout=120) as client:
            with open(wav_path, "rb") as f:
                resp = await client.post(
                    settings.WHISPER_URL,
                    files={"file": f, "video_id": req.videoTitle}
                )
            resp.raise_for_status()
            data = resp.json()

        # 5) 받은 JSON 그대로 반환
        return data
    
    except Exception as e:
        logger.error("Processing error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
