"""Transcribe audio using OpenAI Whisper"""
import whisper
from pathlib import Path
import asyncio

async def transcribe_audio(audio_path: str, language: str = "en") -> dict:
    """
    Transcribe audio using Whisper model
    
    Args:
        audio_path: Path to audio file
        language: Language code (e.g., 'en', 'es', 'fr')
    
    Returns:
        Transcription result with segments
    """
    try:
        # Run whisper in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            _transcribe_with_whisper, 
            audio_path, 
            language
        )
        return result
    
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")

def _transcribe_with_whisper(audio_path: str, language: str) -> dict:
    """Helper function to run Whisper transcription"""
    # Use 'base' model for better accuracy, or 'tiny' for speed
    model = whisper.load_model("base")
    
    result = model.transcribe(
        audio_path,
        language=language,
        verbose=False
    )
    
    return result
