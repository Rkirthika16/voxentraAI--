"""
VoxentraAI Text-to-Speech (TTS) & Conversational Voice Agent Engine.
Synthesizes spoken audio responses in Tamil & English for caller interaction,
IVR telephone dialogue, and citizen audio accessibility.
"""
import io
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import base64

logger = logging.getLogger("voxentra.ai.tts")

# Directory for cached audio responses
TTS_CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "static" / "tts_cache"
TTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)


class TextToSpeechEngine:
    """Generates natural speech audio in Tamil and English for caller interaction."""

    def __init__(self):
        self._gtts_available = False
        try:
            from gtts import gTTS
            self._gtts_available = True
            logger.info("gTTS engine initialized successfully.")
        except ImportError:
            logger.warning("gTTS not installed. Will use Web Speech API fallback.")

    def synthesize_to_bytes(self, text: str, lang: str = "ta") -> Optional[bytes]:
        """
        Synthesizes text into MP3 audio bytes using gTTS.
        Supports 'ta' (Tamil), 'en' (English/Indian accent).
        """
        if not text or not text.strip() or not self._gtts_available:
            return None

        clean_text = text.strip()
        t_lang = "ta" if lang in ["ta", "tamil", "tanglish"] else "en"

        try:
            from gtts import gTTS
            # Use 'co.in' tld for natural Indian English or standard Tamil
            tld = "co.in" if t_lang == "en" else "com"
            tts = gTTS(text=clean_text, lang=t_lang, tld=tld, slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp.read()
        except Exception as e:
            logger.error(f"TTS synthesis error for text '{clean_text[:30]}...': {e}")
            return None

    def synthesize_to_file(self, text: str, filename: str, lang: str = "ta") -> Optional[str]:
        """Synthesizes text and saves to static audio file, returning file path."""
        audio_bytes = self.synthesize_to_bytes(text, lang)
        if not audio_bytes:
            return None

        out_path = TTS_CACHE_DIR / filename
        with open(out_path, "wb") as f:
            f.write(audio_bytes)
        return str(out_path)

    def get_audio_base64_data_url(self, audio_bytes: bytes) -> str:
        """Encodes audio bytes into a playable base64 data URL for browser audio player."""
        b64 = base64.b64encode(audio_bytes).decode("utf-8")
        return f"data:audio/mp3;base64,{b64}"

    def build_caller_conversation(
        self,
        complaint_id: str,
        category: str,
        priority: str,
        department_name_ta: str,
        department_name_en: str,
        lang: str = "ta"
    ) -> Dict[str, Any]:
        """
        Generates bilingual spoken voice script and synthesized audio for AI talking to caller.
        """
        is_ta = lang in ["ta", "tamil", "tanglish"]

        # Formulate department-specific spoken dialogue
        if category == "Police":
            ta_spoken_text = (
                f"வணக்கம், தமிழ்நாடு காவல் மற்றும் அவசர கட்டுப்பாட்டு அறை (100 / 112). "
                f"உங்கள் அவசர புகார் எண் {complaint_id} பதிவு செய்யப்பட்டது. "
                f"உங்கள் பகுதிக்கு அருகிலுள்ள காவல் ரோந்து வாகனத்திற்கு தகவல் அனுப்பப்பட்டு அதிகாரிகள் விரைந்து வருகின்றனர். "
                f"பதற வேண்டாம், பாதுகாப்பான இடத்தில் இருங்கள்."
            )
            en_spoken_text = (
                f"Tamil Nadu Police & Emergency Control Room (100/112). "
                f"Your emergency ticket {complaint_id} is registered with high priority. "
                f"Nearest police patrol unit has been dispatched to your location. "
                f"Officers are responding. Please stay safe."
            )
        elif category == "Electricity":
            ta_spoken_text = (
                f"வணக்கம்! தமிழ்நாடு மின்சார வாரியம் மற்றும் TANGEDCO மின் உதவி மையம் (1912). "
                f"உங்கள் மின்சார புகார் எண் {complaint_id} பதிவு செய்யப்பட்டது. "
                f"மின் பொறியாளர் மற்றும் லைன் ஆய்வாளருக்கு உடனடி நடவடிக்கைக்காக அனுப்பப்பட்டுள்ளது. "
                f"அறுந்து கிடக்கும் மின்கம்பிகள் அருகே செல்ல வேண்டாம். உதவி எண் 1912."
            )
            en_spoken_text = (
                f"TNEB TANGEDCO Electricity Helpline 1912. "
                f"Your power complaint {complaint_id} is registered. "
                f"Zonal maintenance engineers and line inspectors have been dispatched for power restoration. "
                f"Please stay away from live electrical cables."
            )
        elif category == "Water":
            ta_spoken_text = (
                f"வணக்கம்! தமிழ்நாடு குடிநீர் வழங்கல் மற்றும் கழிவுநீரகற்று வாரியம் (1916). "
                f"உங்கள் குடிநீர் புகார் எண் {complaint_id} பதிவு செய்யப்பட்டது. "
                f"வார்டு குடிநீர் உதவி பொறியாளர் மற்றும் குழாய் பராமரிப்பு குழுவிற்கு உடனடி நடவடிக்கைக்காக அனுப்பப்பட்டுள்ளது. உதவி எண் 1916."
            )
            en_spoken_text = (
                f"Tamil Nadu Water Supply & Drainage Board (1916). "
                f"Your water supply grievance {complaint_id} has been registered. "
                f"Zonal pipeline repair engineers have been alerted for inspection."
            )
        elif category == "Roads":
            ta_spoken_text = (
                f"வணக்கம்! தமிழ்நாடு நெடுஞ்சாலைகள் மற்றும் மாநகராட்சி சாலைகள் துறை. "
                f"உங்கள் சாலை சேத புகார் எண் {complaint_id} பதிவு செய்யப்பட்டது. "
                f"நெடுஞ்சாலை உதவி பொறியாளர் மற்றும் சாலை சீரமைப்பு பணிக்குழுவிற்கு தகவல் அனுப்பப்பட்டு நடவடிக்கை எடுக்கப்படுகிறது."
            )
            en_spoken_text = (
                f"Highways Department and Corporation Roads Wing. "
                f"Your road repair ticket {complaint_id} is registered. "
                f"Road maintenance and engineering crew have been assigned to repair the road damage."
            )
        elif category == "Sanitation":
            ta_spoken_text = (
                f"வணக்கம்! நகராட்சி நிர்வாகம் மற்றும் பொது சுகாதாரத் துறை (1913). "
                f"உங்கள் தூய்மை மற்றும் சாக்கடை புகார் எண் {complaint_id} பதிவு செய்யப்பட்டது. "
                f"உங்கள் பகுதி துப்புரவு ஆய்வாளர் மற்றும் தூய்மைப் பணியாளர்களுக்கு உடனடி நடவடிக்கைக்காக அனுப்பப்பட்டுள்ளது."
            )
            en_spoken_text = (
                f"Municipal Administration & Public Health (1913). "
                f"Your sanitation grievance {complaint_id} is registered. "
                f"Zonal sanitary inspector and ground cleaning squad dispatched for immediate clearance."
            )
        else:
            ta_spoken_text = (
                f"வணக்கம்! மாவட்ட ஆட்சியர் அலுவலகம் மற்றும் தமிழ்நாடு அரசு உதவி மையம் (1077). "
                f"உங்கள் புகார் எண் {complaint_id} வெற்றிகரமாக பதிவு செய்யப்பட்டு உரிய துறை அதிகாரிகளுக்கு அனுப்பப்பட்டுள்ளது."
            )
            en_spoken_text = (
                f"Government of Tamil Nadu Public Grievance Helpline (1077). "
                f"Your grievance {complaint_id} has been registered and routed to the competent administrative department for prompt resolution."
            )

        active_script = ta_spoken_text if is_ta else en_spoken_text
        tts_lang = "ta" if is_ta else "en"

        # Synthesize audio bytes
        audio_bytes = self.synthesize_to_bytes(active_script, lang=tts_lang)
        data_url = self.get_audio_base64_data_url(audio_bytes) if audio_bytes else None

        return {
            "spoken_script_ta": ta_spoken_text,
            "spoken_script_en": en_spoken_text,
            "active_script": active_script,
            "language": "tamil" if is_ta else "english",
            "audio_bytes": audio_bytes,
            "audio_data_url": data_url
        }

    def get_ivr_welcome_dialogue(self, lang: str = "ta") -> Dict[str, Any]:
        """Returns the initial spoken greeting when the caller connects to the helpline."""
        is_ta = lang in ["ta", "tamil", "tanglish"]

        ta_greeting = "வணக்கம்! தமிழ்நாடு மின் ஆளுமை பொதுமக்கள் குறைதீர்ப்பு AI உதவி மையத்திற்கு வரவேற்கிறோம். உங்கள் புகாரை கூறுங்கள்."
        en_greeting = "Welcome to Government of Tamil Nadu AI Grievance Helpline. Please state your complaint, location, and department details."

        active = ta_greeting if is_ta else en_greeting
        tts_lang = "ta" if is_ta else "en"

        audio_bytes = self.synthesize_to_bytes(active, lang=tts_lang)
        data_url = self.get_audio_base64_data_url(audio_bytes) if audio_bytes else None

        return {
            "greeting_ta": ta_greeting,
            "greeting_en": en_greeting,
            "active_greeting": active,
            "audio_bytes": audio_bytes,
            "audio_data_url": data_url
        }


def render_autoplay_audio(audio_bytes: bytes, audio_id: str = "ai_voice_player") -> str:
    """Returns HTML5 markup with audio auto-play and visual player controls."""
    if not audio_bytes:
        return ""
    b64 = base64.b64encode(audio_bytes).decode("utf-8")
    return f"""
    <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(56, 189, 248, 0.4); border-radius: 12px; padding: 12px; margin: 10px 0;">
        <div style="font-size: 0.8rem; color: #38bdf8; font-weight: 700; margin-bottom: 6px;">🔊 AI Spoken Voice Response Stream:</div>
        <audio id="{audio_id}" autoplay controls style="width: 100%; border-radius: 8px;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            Your browser does not support HTML5 audio.
        </audio>
    </div>
    """


tts_engine = TextToSpeechEngine()
