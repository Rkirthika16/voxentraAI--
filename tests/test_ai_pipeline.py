import os

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.ai.language_detector import language_detector
from app.ai.nlp_classifier import nlp_classifier
from app.ai.pipeline import ai_pipeline


def test_language_detection_tamil():
    text = "எங்கள் தெருவில் கடந்த 3 நாட்களாக குடிநீர் வரவில்லை."
    lang, conf, dist = language_detector.detect(text)
    assert lang == "tamil"
    assert conf >= 0.7

def test_language_detection_tanglish():
    text = "Anna Nagar la 3 days ah current illa, romba problem ah irukku."
    lang, conf, dist = language_detector.detect(text)
    assert lang == "tanglish"
    assert conf >= 0.65

def test_language_detection_english():
    text = "The street lights in our locality have not been functioning for the past two weeks."
    lang, conf, dist = language_detector.detect(text)
    assert lang == "english"
    assert conf >= 0.7

def test_water_classification_tanglish():
    text = "Kudineer pipe odanju romba thanni waste aaguthu, pressure illa."
    res = ai_pipeline.process_text_complaint(text)
    assert res["category"] == "Water"
    assert res["department_code"] == "TWAD_CMWSSB"

def test_electricity_emergency_priority():
    text = "High voltage live wire arunthu rottula vilundhurukku, spark adikuthu uyirukku aabathu!"
    res = ai_pipeline.process_text_complaint(text)
    assert res["category"] == "Electricity"
    assert res["priority"] == "Emergency"
    assert res["department_code"] == "TANGEDCO"

def test_roads_classification_english():
    text = "Massive dangerous pothole causing frequent bike accidents near the signal."
    res = ai_pipeline.process_text_complaint(text)
    assert res["category"] == "Roads"
    assert res["department_code"] == "HIGHWAYS_CORP"

def test_sanitation_classification_tamil():
    text = "சாக்கடை அடைத்து கழிவுநீர் தெருவில் ஓடுகிறது, கொசு தொல்லை அதிகமாக உள்ளது."
    res = ai_pipeline.process_text_complaint(text)
    assert res["category"] == "Sanitation"
    assert res["department_code"] == "SANITATION_HEALTH"

def test_district_extraction_from_locality():
    text = "Gandhipuram bus stand pakkathula rottula periya pallam irukku."
    res = ai_pipeline.process_text_complaint(text)
    assert res["extracted_district"] == "Coimbatore"


def test_tamil_to_tanglish_transliteration():
    from app.ai.transliteration import tamil_to_tanglish
    ta_text = "அண்ணா நகர் தண்ணீர் வரவில்லை"
    tanglish = tamil_to_tanglish(ta_text)
    assert "Anna Nagar" in tanglish or "thanni" in tanglish or "varala" in tanglish


def test_tanglish_phonetic_normalization():
    from app.ai.transliteration import normalize_tanglish_transcript
    misheard = "under another la three days a current ill"
    normalized = normalize_tanglish_transcript(misheard)
    assert "Anna Nagar" in normalized
    assert "current illa" in normalized

