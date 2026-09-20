"""
VoxentraAI Classifier Bridge.
Provides backward-compatible classifier functions mapped to the modern AI NLP engine.
"""
from typing import Dict, Any
from app.ai.pipeline import ai_pipeline
from app.ai.nlp_classifier import nlp_classifier
from app.ai.language_detector import language_detector

def classify_complaint(text: str) -> Dict[str, Any]:
    """
    Classifies grievance text into Category, Priority, Language, and Department.
    """
    res = ai_pipeline.process(text=text)
    return {
        "category": res.get("category", "Other"),
        "priority": res.get("priority", "Medium"),
        "language": res.get("language", "tamil"),
        "district": res.get("district"),
        "confidence": res.get("confidence", 0.9)
    }

class DummyModel:
    """Mock model to satisfy legacy joblib load references."""
    def predict(self, X):
        return ["Other"]

model = DummyModel()
