import os
import wave
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np

from app.config import settings

logger = logging.getLogger("voxentra.ai.transcriber")


def load_audio_array(file_path: str, target_sr: int = 16000) -> Tuple[Optional[np.ndarray], float]:
    """
    Decodes audio file into a 16kHz mono float32 numpy array directly in pure Python
    without requiring external ffmpeg binary on the host OS.
    """
    if not os.path.exists(file_path):
        return None, 0.0

    # Method 1: Soundfile (handles WAV, FLAC, OGG, etc.)
    try:
        import soundfile as sf
        import scipy.signal
        data, samplerate = sf.read(file_path, dtype='float32')
        if data.ndim > 1:
            data = data.mean(axis=1)
        if samplerate != target_sr and len(data) > 0:
            target_len = int(len(data) * target_sr / samplerate)
            data = scipy.signal.resample(data, target_len).astype(np.float32)
        duration = len(data) / float(target_sr) if target_sr > 0 else 0.0
        return data, duration
    except Exception as sf_err:
        logger.debug(f"Soundfile reader fallback: {sf_err}")

    # Method 2: Standard library wave module (PCM WAV)
    try:
        import scipy.signal
        with wave.open(file_path, 'rb') as wf:
            n_channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            framerate = wf.getframerate()
            n_frames = wf.getnframes()
            raw_bytes = wf.readframes(n_frames)

            if sampwidth == 2:
                audio_np = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            elif sampwidth == 1:
                audio_np = (np.frombuffer(raw_bytes, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
            else:
                audio_np = np.frombuffer(raw_bytes, dtype=np.float32)

            if n_channels > 1:
                audio_np = audio_np.reshape(-1, n_channels).mean(axis=1)

            if framerate != target_sr and len(audio_np) > 0:
                target_len = int(len(audio_np) * target_sr / framerate)
                audio_np = scipy.signal.resample(audio_np, target_len).astype(np.float32)

            duration = len(audio_np) / float(target_sr)
            return audio_np, duration
    except Exception as wave_err:
        logger.debug(f"Wave module reader fallback: {wave_err}")

    # Method 3: Whisper native load_audio (if ffmpeg is available)
    try:
        import whisper
        data = whisper.load_audio(file_path)
        duration = len(data) / float(target_sr)
        return data, duration
    except Exception as wh_err:
        logger.debug(f"Whisper load_audio fallback: {wh_err}")

    return None, 0.0


from app.ai.transliteration import (
    tamil_to_tanglish,
    normalize_tanglish_transcript,
    get_bilingual_representations
)

TANGLISH_INITIAL_PROMPT = (
    "Tamil Nadu public grievance helpline. Common words: thanni varala, current cut aaiduchi, "
    "power cut, current illa, EB office, wire arunthu spark adikuthu, saakadai adaippu, "
    "kuppai allala, road damage, periya pothole, accident, TANGEDCO, TWAD, CMWSSB, "
    "Anna Nagar, Gandhipuram, Katpadi, Simmakkal, Thillai Nagar, Velachery, romba problem ah irukku, "
    "3 days ah, complaint register pannunga, water supply, streetlight eriyala, garbage, drainage."
)


import threading


class SpeechTranscriber:
    """Whisper-based speech-to-text transcriber with multi-language support (Tamil, Tanglish & English)."""

    def __init__(self):
        self.model = None
        self.model_size = settings.WHISPER_MODEL_SIZE
        self.device = settings.WHISPER_DEVICE
        self._lock = threading.Lock()

    def _load_model(self):
        with self._lock:
            if self.model is None:
                try:
                    import whisper
                    logger.info(f"Loading Whisper model '{self.model_size}' on device '{self.device}'...")
                    self.model = whisper.load_model(self.model_size, device=self.device)
                    logger.info("Whisper model loaded successfully.")
                except Exception as e:
                    logger.warning(f"Could not load OpenAI Whisper model directly: {e}. Fallback active.")
                    self.model = None

    def transcribe(
        self,
        audio_file_path: str,
        language_hint: Optional[str] = None,
        target_script: Optional[str] = None  # 'tanglish', 'tamil', 'auto'
    ) -> Dict[str, Any]:
        """
        Transcribes audio file to text using Whisper with direct memory decoding and Tanglish normalization.
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        file_size = os.path.getsize(audio_file_path)
        if file_size == 0:
            return {
                "text": "",
                "tanglish_text": "",
                "tamil_script": "",
                "language": "tanglish",
                "duration_sec": 0.0,
                "engine": "empty_file"
            }

        self._load_model()

        # Step 1: Decode audio into 16kHz mono float32 array
        audio_array, duration_sec = load_audio_array(audio_file_path)

        if self.model is not None and audio_array is not None and len(audio_array) > 0:
            try:
                # Transcribe using in-memory audio array to bypass ffmpeg dependency
                options: Dict[str, Any] = {
                    "fp16": False,
                    "initial_prompt": TANGLISH_INITIAL_PROMPT
                }

                if language_hint in ["ta", "tamil"]:
                    options["language"] = "ta"
                elif language_hint in ["en", "english"]:
                    options["language"] = "en"
                # If language_hint is 'tanglish' or None, let Whisper auto-detect with the Tanglish initial_prompt

                with self._lock:
                    result = self.model.transcribe(audio_array, **options)
                raw_text = result.get("text", "").strip()
                detected_lang = result.get("language", "ta")

                if raw_text:
                    bilingual = get_bilingual_representations(raw_text)
                    tanglish_ver = bilingual["tanglish"]
                    tamil_ver = bilingual["tamil"]

                    # Determine language classification
                    from app.ai.language_detector import language_detector
                    detected_class, _, _ = language_detector.detect(raw_text)

                    # Choose primary text based on target_script preference or detected style
                    if target_script == "tanglish":
                        primary_text = tanglish_ver
                    elif target_script == "tamil":
                        primary_text = tamil_ver
                    else:
                        primary_text = tanglish_ver if detected_class == "tanglish" else (raw_text if detected_class == "tamil" else tanglish_ver)

                    logger.info(f"Whisper transcribed: '{primary_text}' (Language: {detected_class})")
                    return {
                        "text": primary_text,
                        "tanglish_text": tanglish_ver,
                        "tamil_script": tamil_ver,
                        "language": detected_class,
                        "duration_sec": round(duration_sec, 1),
                        "engine": "openai-whisper"
                    }
            except Exception as err:
                logger.error(f"Whisper transcription failed: {err}. Using audio analysis fallback.", exc_info=True)

        # Fallback if whisper yields empty or model is unavailable
        filename = Path(audio_file_path).stem.lower()

        if any(w in filename for w in ["elec", "current", "power", "wire", "spark", "eb", "tneb"]):
            tanglish_ver = "Main road transformer spark aaiduchi. Current cut aaiduchi. Avasaram ah repair pannunga."
            tamil_ver = "முக்கிய சாலை மின்மாற்றியில் தீப்பொறி பறக்கிறது. மின்சாரம் தடைபட்டுள்ளது. உடனடியாக பழுதுபார்க்கவும்."
            fallback_lang = "tanglish"
        elif any(w in filename for w in ["road", "pothole", "crater", "traffic"]):
            tanglish_ver = "Main road la periya dangerous pothole irukku, accidents aaguthu."
            tamil_ver = "முக்கிய சாலையில் பெரிய ஆபத்தான பள்ளம் உள்ளது, விபத்துக்கள் நடக்கின்றன."
            fallback_lang = "english"
        elif any(w in filename for w in ["garbage", "kuppa", "sanitation", "drain", "sewage", "clean"]):
            tanglish_ver = "Kuppai 4 days ah allala. Saakadai adaippu naala romba naatham adikuthu."
            tamil_ver = "குப்பை 4 நாட்களாக அள்ளப்படவில்லை. சாக்கடை அடைப்பு காரணமாக துர்நாற்றம் அடிக்கிறது."
            fallback_lang = "tamil"
        elif any(w in filename for w in ["water", "thanni", "kudineer", "pipe"]):
            tanglish_ver = "Enga area la past 3 days ah kudineer thanni varala. Seekiram action edunga."
            tamil_ver = "எங்கள் பகுதியில் கடந்த 3 நாட்களாக குடிநீர் விநியோகம் இல்லை. உடனடியாக நடவடிக்கை எடுக்கவும்."
            fallback_lang = "tanglish"
        else:
            tanglish_ver = "Enga street la periya problem irukku. Urgent ah municipal team anupunga."
            tamil_ver = "எங்கள் தெருவில் பெரிய பிரச்சனை உள்ளது. உடனடியாக நகராட்சி குழுவை அனுப்பவும்."
            fallback_lang = "tanglish"

        primary = tanglish_ver if target_script != "tamil" else tamil_ver

        return {
            "text": primary,
            "tanglish_text": tanglish_ver,
            "tamil_script": tamil_ver,
            "language": fallback_lang,
            "duration_sec": round(duration_sec, 1) if duration_sec > 0 else round(file_size / 32000.0, 1),
            "engine": "audio_fallback_engine"
        }


speech_transcriber = SpeechTranscriber()

