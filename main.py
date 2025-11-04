from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
from pathlib import Path
from typing import Optional

from modules.audio_downloader import download_audio
from modules.transcriber import transcribe_audio
from modules.srt_converter import create_srt_file

# Create necessary directories
UPLOADS_DIR = Path("uploads")
DOWNLOADS_DIR = Path("downloads")
UPLOADS_DIR.mkdir(exist_ok=True)
DOWNLOADS_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Video Transcription API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve downloaded files
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

# Request model
class TranscribeRequest(BaseModel):
    url: str
    target_language: Optional[str] = "en"

# Response model
class TranscribeResponse(BaseModel):
    status: str
    message: str
    download_url: Optional[str] = None
    job_id: Optional[str] = None

def cleanup_files(job_id: str):
    """Cleanup temporary files after some time"""
    import time
    time.sleep(3600)  # Keep files for 1 hour
    audio_path = UPLOADS_DIR / f"{job_id}.wav"
    if audio_path.exists():
        audio_path.unlink()

@app.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(request: TranscribeRequest, background_tasks: BackgroundTasks):
    """
    Transcribe a video from URL and return SRT file
    
    Args:
        url: Video URL (YouTube, etc.)
        target_language: Target language for transcription (default: en)
    
    Returns:
        JSON with download_url to SRT file
    """
    try:
        job_id = str(uuid.uuid4())[:8]
        
        # Download audio
        print(f"[{job_id}] Downloading audio from {request.url}")
        audio_path = await download_audio(request.url, job_id, UPLOADS_DIR)
        
        # Transcribe audio
        print(f"[{job_id}] Transcribing audio...")
        transcription_result = await transcribe_audio(str(audio_path), request.target_language)
        
        # Convert to SRT
        print(f"[{job_id}] Converting to SRT format...")
        srt_path = create_srt_file(transcription_result, job_id, DOWNLOADS_DIR)
        
        # Schedule cleanup
        background_tasks.add_task(cleanup_files, job_id)
        
        download_url = f"/downloads/{srt_path.name}"
        
        return TranscribeResponse(
            status="success",
            message="Transcription completed successfully",
            download_url=download_url,
            job_id=job_id
        )
    
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download SRT file"""
    file_path = DOWNLOADS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
