"""Download audio from video URLs using yt-dlp"""
import yt_dlp
from pathlib import Path
import asyncio

async def download_audio(url: str, job_id: str, output_dir: Path) -> Path:
    """
    Download audio from video URL using yt-dlp
    
    Args:
        url: Video URL (YouTube, etc.)
        job_id: Unique job identifier
        output_dir: Directory to save audio files
    
    Returns:
        Path to downloaded audio file
    """
    output_path = output_dir / f"{job_id}.wav"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': str(output_dir / job_id),
        'quiet': False,
        'no_warnings': False,
    }
    
    try:
        # Run yt-dlp in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _download_with_ydl, url, ydl_opts)
        
        if not output_path.exists():
            raise Exception(f"Audio file not created at {output_path}")
        
        return output_path
    
    except Exception as e:
        raise Exception(f"Failed to download audio: {str(e)}")

def _download_with_ydl(url: str, opts: dict):
    """Helper function to run yt-dlp"""
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.extract_info(url, download=True)
