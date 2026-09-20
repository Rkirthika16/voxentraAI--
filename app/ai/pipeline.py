import logging
from typing import Dict, Any, Optional
from app.ai.language_detector import language_detector
from app.ai.nlp_classifier import nlp_classifier
from app.ai.transcriber import speech_transcriber

logger = logging.getLogger("voxentra.ai.pipeline")

class AIPipeline:
    """Master AI engine coordinating Speech-to-Text, Language Detection, and NLP Classification."""

    def __init__(self):
        self.transcriber = speech_transcriber
        self.language_detector = language_detector
        self.classifier = nlp_classifier

    def process_text_complaint(
        self,
        text: str,
        explicit_district: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes a raw text grievance string (Tamil, English, or Tanglish).
        """
        clean_text = text.strip() if text else ""
        
        # 1. Language Detection
        detected_lang, lang_conf, lang_dist = self.language_detector.detect(clean_text)
        
        # 2. NLP Classification & Urgency Assessment
        analysis = self.classifier.analyze(
            text=clean_text,
            detected_language=detected_lang,
            explicit_district=explicit_district
        )

        overall_confidence = round((lang_conf * 0.4) + (analysis["confidence_score"] * 0.6), 2)

        return {
            "original_text": clean_text,
            "transcribed_text": None,
            "detected_language": detected_lang,
            "language_confidence": lang_conf,
            "language_distribution": lang_dist,
            "category": analysis["category"],
            "priority": analysis["priority"],
            "confidence_score": overall_confidence,
            "matched_keywords": analysis["matched_keywords"],
            "urgency_reason": analysis["urgency_reason"],
            "extracted_district": analysis["extracted_district"],
            "department_code": analysis["department_code"],
            "department_name_en": analysis["department_name_en"],
            "department_name_ta": analysis["department_name_ta"],
            "department_helpline": analysis["department_helpline"]
        }

    def process_voice_complaint(
        self,
        audio_file_path: str,
        explicit_district: Optional[str] = None,
        language_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes an audio voice grievance (transcription -> language -> classification).
        """
        # 1. Speech-to-Text Transcription
        transcription_res = self.transcriber.transcribe(
            audio_file_path=audio_file_path,
            language_hint=language_hint
        )
        transcribed_text = transcription_res.get("text", "")
        audio_duration = transcription_res.get("duration_sec", 0.0)

        # 2. Process resulting text through standard NLP pipeline
        nlp_result = self.process_text_complaint(
            text=transcribed_text,
            explicit_district=explicit_district
        )

        # Add voice-specific fields
        nlp_result["transcribed_text"] = transcribed_text
        nlp_result["audio_duration_sec"] = audio_duration
        nlp_result["stt_engine"] = transcription_res.get("engine", "whisper")

        return nlp_result

ai_pipeline = AIPipeline()
