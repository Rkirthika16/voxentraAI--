import re
from typing import Tuple, Dict

# Tamil Unicode range: U+0B80 to U+0BFF
TAMIL_CHAR_PATTERN = re.compile(r"[\u0B80-\u0BFF]")

# Common Tanglish marker words, phonemes, and colloquial expressions
TANGLISH_VOCABULARY = {
    # Nouns / Verbs / Adverbs
    "thanni", "kudineer", "current", "karand", "poyiduchu", "poiruchi", "poiduchi",
    "aaiduchu", "aayiduchu", "aachu", "aairukku", "irukku", "illa", "illai",
    "varala", "vara", "varale", "maatikidhu", "maatudhu", "romba", "periya", "chinna",
    "theru", "theruvil", "veedu", "veetla", "veetula", "oorla", "engalukku", "enga",
    "yenga", "eppo", "yaarukitta", "pannunga", "pannungalen", "seiyunga", "seiyala",
    "mudiyala", "odanju", "odanjirukku", "udanjiduchu", "odanchiduchu", "saakadai",
    "kuppai", "kupa", "naatham", "smell", "adikuthu", "eriyala", "light", "vilakku",
    "maram", "vilundhruchu", "kombu", "odanjiduchu", "kambam", "pillar", "wire",
    "arunthu", "arnju", "thonguthu", "spark", "vedichuduchu", "thee", "neruppu",
    "uyir", "aabathu", "paathu", "sikkaram", "seekiram", "udane", "avachiyam",
    "avasaram", "thanneer", "kuzhai", "tap", "kuzhaai", "pipe", "leak", "leakaaguthu",
    "overflow", "valiyudhu", "vazhiyudhu", "rottula", "roadla", "pallam", "gundu",
    "kuzhi", "accident", "aaguthu", "nadakka", "mudila", "poga", "mudila", "vandi",
    "pochu", "vandhurukku", "edukala", "allala", "clean", "pannala", "nasungirukku",
    "complaint", "kuduthom", "solliyum", "nadakkala", "neram", "mani", "naal", "naala",
    "naalaikku", "innum", "varave", "illa", "kaapaathunga", "vanakkam", "aiyya", "sir"
}

# Tanglish characteristic suffixes (e.g. road-la, veet-oda, mudiy-ala)
TANGLISH_SUFFIXES = (
    "la", "le", "oda", "kku", "ukku", "aachu", "irukku", "nga", "dhu", "chi", "chu",
    "aaga", "aagi", "padu", "kitta", "lerundhu", "lirundhu"
)

class LanguageDetector:
    """Accurately detects Tamil script, Tanglish (Tamil in Latin alphabet), or English."""

    @staticmethod
    def detect(text: str) -> Tuple[str, float, Dict[str, float]]:
        """
        Analyzes input text and returns:
        - Primary language string: 'tamil', 'tanglish', or 'english'
        - Confidence score: float between 0.0 and 1.0
        - Detailed score distribution dict
        """
        if not text or not text.strip():
            return "tamil", 0.5, {"tamil": 0.5, "tanglish": 0.25, "english": 0.25}

        clean_text = text.strip()
        total_chars = len(clean_text)
        tamil_chars = len(TAMIL_CHAR_PATTERN.findall(clean_text))

        # Check for direct Tamil Unicode script
        tamil_script_ratio = tamil_chars / total_chars if total_chars > 0 else 0
        if tamil_script_ratio > 0.15:
            confidence = min(0.99, 0.70 + (tamil_script_ratio * 0.3))
            return "tamil", round(confidence, 2), {
                "tamil": round(confidence, 2),
                "tanglish": 0.05,
                "english": round(1.0 - confidence - 0.05, 2)
            }

        # For Latin script, analyze words and tokens
        words = re.findall(r"\b[a-zA-Z]+\b", clean_text.lower())
        if not words:
            return "english", 0.5, {"tamil": 0.0, "tanglish": 0.0, "english": 1.0}

        tanglish_word_count = 0
        tanglish_suffix_count = 0

        for word in words:
            if word in TANGLISH_VOCABULARY:
                tanglish_word_count += 1
            else:
                # Suffix check if word is long enough
                if len(word) >= 5 and any(word.endswith(suffix) for suffix in TANGLISH_SUFFIXES):
                    tanglish_suffix_count += 1

        tanglish_signals = tanglish_word_count + (tanglish_suffix_count * 0.5)
        tanglish_ratio = tanglish_signals / len(words)

        # Classify as Tanglish if sufficient Tamil phonetic markers exist
        if tanglish_ratio >= 0.18 or (len(words) <= 4 and tanglish_word_count >= 1):
            confidence = min(0.98, 0.65 + (tanglish_ratio * 0.35))
            return "tanglish", round(confidence, 2), {
                "tanglish": round(confidence, 2),
                "english": round(1.0 - confidence, 2),
                "tamil": 0.0
            }

        # Otherwise English
        confidence = min(0.98, 0.75 + (1.0 - tanglish_ratio) * 0.2)
        return "english", round(confidence, 2), {
            "english": round(confidence, 2),
            "tanglish": round(1.0 - confidence, 2),
            "tamil": 0.0
        }

language_detector = LanguageDetector()
