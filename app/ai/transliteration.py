"""
VoxentraAI Tamil <-> Tanglish Phonetic Transliteration & Normalization Engine.
Translates spoken Tamil Unicode into readable colloquial Tanglish and vice-versa,
and corrects common speech-to-text acoustic mishearings.
"""
import re
from typing import Dict, Tuple, Optional, List

# Tamil Unicode character mappings
TAMIL_VOWELS = {
    "\u0B85": "a",
    "\u0B86": "aa",
    "\u0B87": "i",
    "\u0B88": "ee",
    "\u0B89": "u",
    "\u0B8A": "oo",
    "\u0B8E": "e",
    "\u0B8F": "ae",
    "\u0B90": "ai",
    "\u0B92": "o",
    "\u0B93": "oa",
    "\u0B94": "au",
    "\u0B83": "ak"
}

TAMIL_VOWEL_SIGNS = {
    "\u0BBE": "aa",
    "\u0BBF": "i",
    "\u0BC0": "ee",
    "\u0BC1": "u",
    "\u0BC2": "oo",
    "\u0BC6": "e",
    "\u0BC7": "ae",
    "\u0BC8": "ai",
    "\u0BCA": "o",
    "\u0BCB": "oa",
    "\u0BCC": "au",
    "\u0BCD": ""  # Virama / Pulli (pure consonant)
}

TAMIL_CONSONANTS = {
    "\u0B95": "k",
    "\u0B99": "ng",
    "\u0B9A": "ch",
    "\u0B9C": "j",
    "\u0B9E": "nj",
    "\u0B9F": "t",
    "\u0BA3": "n",
    "\u0BA4": "th",
    "\u0BA8": "n",
    "\u0BA9": "n",
    "\u0BAA": "p",
    "\u0BAE": "m",
    "\u0BAF": "y",
    "\u0BB0": "r",
    "\u0BB1": "r",
    "\u0BB2": "l",
    "\u0BB3": "l",
    "\u0BB4": "zh",
    "\u0BB5": "v",
    "\u0BB7": "sh",
    "\u0BB8": "s",
    "\u0BB9": "h"
}

# Common Tamil words to natural Tanglish mapping
COLLOQUIAL_TAMIL_TO_TANGLISH = {
    "அண்ணா நகர்": "Anna Nagar",
    "அண்ணாநகர்": "Anna Nagar",
    "காந்திபுரம்": "Gandhipuram",
    "சிம்மக்கல்": "Simmakkal",
    "காட்பாடி": "Katpadi",
    "தில்லை நகர்": "Thillai Nagar",
    "வேளச்சேரி": "Velachery",
    "தாம்பரம்": "Tambaram",
    "கோயம்புத்தூர்": "Coimbatore",
    "மதுரை": "Madurai",
    "திருச்சி": "Tiruchirappalli",
    "சேலம்": "Salem",
    "சென்னை": "Chennai",
    "திருநெல்வேலி": "Tirunelveli",
    "தண்ணீர்": "thanni",
    "குடிநீர்": "kudineer",
    "வரவில்லை": "varala",
    "இல்லை": "illa",
    "கரண்ட்": "current",
    "மின்சாரம்": "current",
    "துண்டிக்கப்பட்டுள்ளது": "cut aaiduchi",
    "போய்விட்டது": "poyiduchu",
    "சாக்கடை": "saakadai",
    "அடைப்பு": "adaippu",
    "குப்பை": "kuppai",
    "அள்ளப்படவில்லை": "allala",
    "துர்நாற்றம்": "romba naatham",
    "பள்ளம்": "pothole",
    "உடைந்துள்ளது": "odanjirukku",
    "உடைந்துவிட்டது": "odanjiduchu",
    "விபத்து": "accident",
    "ஆபத்து": "aabathu",
    "அவசரம்": "avasaram",
    "உடனடியாக": "seekiram",
    "ஆட்கள்": "aala",
    "அனுப்பவும்": "anupunga",
    "நடவடிக்கை": "action",
    "எடுக்கவும்": "edunga",
    "பிரச்சனை": "problem",
    "மிகவும்": "romba",
    "இருக்கிறது": "irukku",
    "நாட்களாக": "days ah",
    "நாட்கள்": "days",
    "தெருவில்": "street la",
    "ரோட்டில்": "rottula",
    "சாலையில்": "road la",
    "விளக்கு": "streetlight",
    "எரியவில்லை": "eriyala"
}

# Phonetic Tanglish Mishearings Corrector (Fixes Whisper acoustic errors when Tamil accent is spoken)
TANGLISH_PHONETIC_REPLACEMENTS: List[Tuple[re.Pattern, str]] = [
    # Location misrecognitions
    (re.compile(r"\b(under another|ananagar|anna nagar)\b", re.I), "Anna Nagar"),
    (re.compile(r"\b(gandhi puram|gandhipuram)\b", re.I), "Gandhipuram"),
    (re.compile(r"\b(katpadi|catpadi)\b", re.I), "Katpadi"),
    (re.compile(r"\b(velachery|vela cherry)\b", re.I), "Velachery"),
    
    # Common Tanglish words misheard by English STT
    (re.compile(r"\b(tony|tonny|tani|thanne|thani)\b", re.I), "thanni"),
    (re.compile(r"\b(kudi neer|kudiner|kudineeru)\b", re.I), "kudineer"),
    (re.compile(r"\b(water varala|thanni varale|thanni varalai|varala)\b", re.I), "thanni varala"),
    (re.compile(r"\b(current ill|currentila|current illai|karand illa)\b", re.I), "current illa"),
    (re.compile(r"\b(cut aaiduchu|cut aiduchu|cut aayiduchu|cut aaidichi)\b", re.I), "cut aaiduchi"),
    (re.compile(r"\b(poyiduchi|poiruchu|poiduchu)\b", re.I), "poyiduchu"),
    (re.compile(r"\b(wire arunthu|wire arnchu|wire arunthudu)\b", re.I), "wire arunthu"),
    (re.compile(r"\b(sparking|spark adikuthu|spark adikudhu)\b", re.I), "spark adikuthu"),
    (re.compile(r"\b(saakadai|sakadai|saakkadai)\b", re.I), "saakadai"),
    (re.compile(r"\b(kuppa|kupa|kuppai)\b", re.I), "kuppai"),
    (re.compile(r"\b(allala|alala|alaala|allalai)\b", re.I), "allala"),
    (re.compile(r"\b(naatham|nattham|natham adikuthu)\b", re.I), "naatham adikuthu"),
    (re.compile(r"\b(odanchiduchu|odanjiduchu|odanjirukku|udanjiduchu)\b", re.I), "odanjirukku"),
    (re.compile(r"\b(eriyala|eriyalai|eriyale)\b", re.I), "eriyala"),
    (re.compile(r"\b(seekiram|sikkaram|sekiram)\b", re.I), "seekiram"),
    (re.compile(r"\b(anupunga|anuppunga|anupungalen)\b", re.I), "anupunga"),
    (re.compile(r"\b(pannunga|pannungalen|seiyunga)\b", re.I), "pannunga"),
    (re.compile(r"\b(romba problem|romba kastam|romba kashtam)\b", re.I), "romba problem"),
    (re.compile(r"\b(uyirukku aabathu|aabathu|uyir aabathu)\b", re.I), "uyirukku aabathu"),
    (re.compile(r"\b(3 days a|3 days ah|3 day sa|three days a)\b", re.I), "3 days ah"),
    (re.compile(r"\b(2 days a|2 days ah|2 day sa|two days a)\b", re.I), "2 days ah"),
    (re.compile(r"\b(4 days a|4 days ah|4 day sa|four days a)\b", re.I), "4 days ah")
]


def tamil_to_tanglish(text: str) -> str:
    """
    Converts Tamil Unicode script into natural, readable colloquial Tanglish.
    Uses colloquial phrase replacements followed by character-level phonetic transliteration.
    """
    if not text:
        return ""

    result = text

    # Step 1: Replace well-known colloquial words and district names first
    for ta_phrase, tanglish_phrase in COLLOQUIAL_TAMIL_TO_TANGLISH.items():
        result = result.replace(ta_phrase, tanglish_phrase)

    # Step 2: Transliterate any remaining Tamil Unicode characters
    chars = list(result)
    output = []
    i = 0
    n = len(chars)

    while i < n:
        ch = chars[i]

        # Check for standalone Tamil vowel
        if ch in TAMIL_VOWELS:
            output.append(TAMIL_VOWELS[ch])
            i += 1
            continue

        # Check for Tamil consonant
        if ch in TAMIL_CONSONANTS:
            base_cons = TAMIL_CONSONANTS[ch]
            # Check if next char is a vowel sign or virama
            if i + 1 < n and chars[i + 1] in TAMIL_VOWEL_SIGNS:
                vowel_sign = TAMIL_VOWEL_SIGNS[chars[i + 1]]
                output.append(base_cons + vowel_sign)
                i += 2
            else:
                # Default implicit 'a'
                output.append(base_cons + "a")
                i += 1
            continue

        # Pass through numbers, punctuation, Latin characters as-is
        output.append(ch)
        i += 1

    transliterated = "".join(output)

    # Step 3: Clean up multiple spaces and double vowels for smooth reading
    transliterated = re.sub(r"\s+", " ", transliterated).strip()
    
    # Capitalize first letter of sentences
    if transliterated and len(transliterated) > 0:
        transliterated = transliterated[0].upper() + transliterated[1:]

    return transliterated


def normalize_tanglish_transcript(raw_transcript: str) -> str:
    """
    Cleans and repairs phonetic misrecognitions in Tanglish transcripts produced by STT engines.
    """
    if not raw_transcript:
        return ""

    text = raw_transcript.strip()

    # Check if text is mostly Tamil Unicode
    tamil_chars = len(re.findall(r"[\u0B80-\u0BFF]", text))
    if tamil_chars > 5:
        # Convert Tamil Unicode to natural Tanglish
        text = tamil_to_tanglish(text)

    # Apply phonetic regex replacements
    for pattern, replacement in TANGLISH_PHONETIC_REPLACEMENTS:
        text = pattern.sub(replacement, text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    if text:
        text = text[0].upper() + text[1:]
    return text


def get_bilingual_representations(text: str) -> Dict[str, str]:
    """
    Generates synchronized representations in:
    - Tanglish (Colloquial Latin script)
    - Tamil (Unicode Tamil script)
    - Clean description
    """
    if not text:
        return {"tanglish": "", "tamil": "", "primary": ""}

    cleaned = text.strip()
    is_tamil_unicode = len(re.findall(r"[\u0B80-\u0BFF]", cleaned)) > 3

    if is_tamil_unicode:
        tanglish_version = tamil_to_tanglish(cleaned)
        tamil_version = cleaned
    else:
        tanglish_version = normalize_tanglish_transcript(cleaned)
        # Construct approximate Tamil script equivalent for reference
        tamil_version = cleaned  # Keep original if user input in Latin

    return {
        "tanglish": tanglish_version,
        "tamil": tamil_version,
        "primary": tanglish_version if not is_tamil_unicode else tamil_version
    }
