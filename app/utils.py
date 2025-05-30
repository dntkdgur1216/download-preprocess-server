import os, shutil, logging, yt_dlp, ffmpeg
from pytube import YouTube
from fastapi import HTTPException

logger = logging.getLogger("processor.utils")

def init_cache(tmp_root: str, policy: str):
    cache = os.path.join(tmp_root, "cache")
    if policy == "always" and os.path.exists(cache):
        shutil.rmtree(cache)
    os.makedirs(cache, exist_ok=True)
    return cache

def download_audio(url: str, cache_dir: str, policy: str) -> str:
    mp4_path = os.path.join(cache_dir, "audio.mp4")
    if policy == "always" or not os.path.exists(mp4_path):
        opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": os.path.join(cache_dir, "audio.%(ext)s"),
            "quiet": True,
            # 직접 추출해 둔 쿠키 파일을 사용
            "cookiefile": "/home/ec2-user/download-preprocess-server/cookies.txt",
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
        ext = info.get("ext","m4a")
        mp4_path = os.path.join(cache_dir, f"audio.{ext}")
        logger.info(f"Downloaded audio to {mp4_path}")
    return mp4_path

def convert_to_wav(mp4_path: str, wav_path: str):
    try:
        (
            ffmpeg.input(mp4_path)
                  .output(wav_path, format="wav",
                          acodec="pcm_s16le", ac=1, ar="16k")
                  .run(overwrite_output=True)
        )
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"ffmpeg error: {e}")
    return wav_path

def cleanup_file(path: str):
    try:
        os.remove(path)
    except OSError:
        pass
