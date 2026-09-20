import os
import uuid
import wave
import struct
import math
from pathlib import Path
from typing import Optional
from app.config import UPLOAD_DIR

def save_upload_audio_file(file_bytes: bytes, original_filename: Optional[str] = None) -> str:
    """
    Saves an uploaded audio file buffer to the uploads directory.
    Returns the absolute file path.
    """
    ext = ".wav"
    if original_filename:
        _, original_ext = os.path.splitext(original_filename)
        if original_ext.lower() in [".wav", ".mp3", ".ogg", ".m4a", ".flac", ".webm"]:
            ext = original_ext.lower()

    unique_filename = f"audio_{uuid.uuid4().hex[:12]}{ext}"
    target_path = UPLOAD_DIR / unique_filename
    
    with open(target_path, "wb") as f:
        f.write(file_bytes)
        
    return str(target_path)

def create_synthetic_test_wav(
    output_path: str,
    duration_sec: float = 2.0,
    frequency: float = 440.0,
    sample_rate: int = 16000
) -> str:
    """
    Generates a clean synthetic PCM WAV file for unit tests or telephony simulations.
    """
    num_samples = int(duration_sec * sample_rate)
    with wave.open(output_path, "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            value = int(32767.0 * 0.5 * math.sin(2.0 * math.pi * frequency * t))
            data = struct.pack("<h", value)
            wav_file.writeframes(data)
            
    return output_path
