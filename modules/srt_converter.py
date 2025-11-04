"""Convert Whisper transcription to SRT format"""
from pathlib import Path
from typing import Dict, List

def create_srt_file(transcription: Dict, job_id: str, output_dir: Path) -> Path:
    """
    Convert Whisper transcription to SRT format
    
    Args:
        transcription: Whisper transcription result
        job_id: Unique job identifier
        output_dir: Directory to save SRT file
    
    Returns:
        Path to created SRT file
    """
    output_path = output_dir / f"{job_id}.srt"
    
    srt_content = _generate_srt(transcription['segments'])
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(srt_content)
    
    return output_path

def _generate_srt(segments: List[Dict]) -> str:
    """
    Generate SRT content from segments
    
    SRT format:
    1
    00:00:00,000 --> 00:00:05,000
    First subtitle text
    
    2
    00:00:05,000 --> 00:00:10,000
    Second subtitle text
    """
    srt_lines = []
    
    for idx, segment in enumerate(segments, 1):
        start_time = _format_timestamp(segment['start'])
        end_time = _format_timestamp(segment['end'])
        text = segment['text'].strip()
        
        if text:  # Only add non-empty segments
            srt_lines.append(str(idx))
            srt_lines.append(f"{start_time} --> {end_time}")
            srt_lines.append(text)
            srt_lines.append("")  # Blank line between subtitles
    
    return "\n".join(srt_lines)

def _format_timestamp(seconds: float) -> str:
    """
    Convert seconds to SRT timestamp format (HH:MM:SS,mmm)
    
    Args:
        seconds: Time in seconds
    
    Returns:
        Formatted timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
