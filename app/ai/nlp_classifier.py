"""
VoxentraAI Multilingual NLP Grievance Classifier.
Accurately categorizes public grievances in Tamil script, Tanglish, and English
into Water, Electricity, Roads, Sanitation, and Other with high-precision urgency triage.
"""
import re
from typing import Dict, Any, List, Optional, Tuple
from app.config import (
    TAMIL_NADU_DISTRICTS,
    TAMIL_NADU_DEPARTMENTS,
    CATEGORIES,
    PRIORITY_LEVELS
)

# Comprehensive category lexicons with weights
CATEGORY_PATTERNS: Dict[str, List[Tuple[str, float]]] = {
    "Police": [
        # Police, crime, safety, 100 control room, accidents, emergency help
        ("police", 5.0), ("100 calling", 5.0), ("control room", 5.0), ("police station", 5.0),
        ("theft", 5.0), ("thirudan", 5.0), ("thiruttu", 5.0), ("robbery", 5.0), ("kollai", 5.0),
        ("chain snatching", 5.2), ("snatching", 5.0), ("murder", 5.5), ("kolai", 5.5),
        ("accident", 5.0), ("vibathu", 5.0), ("road accident", 5.2), ("hit and run", 5.2),
        ("fight", 4.8), ("sanda", 4.8), ("adithadi", 5.0), ("attack", 5.0), ("harassment", 5.0),
        ("eve teasing", 5.0), ("women safety", 5.0), ("penkal paathukaapu", 5.0), ("threat", 4.8),
        ("bayama irukku", 4.5), ("help pannunga police", 5.2), ("police venum", 5.2), ("police anupunga", 5.2),
        ("patrol vehicle", 5.0), ("pcr van", 5.0), ("missing", 4.8), ("kaanaamal", 5.0),
        ("kidnap", 5.5), ("kadathal", 5.5), ("drugs", 4.8), ("ganja", 5.0), ("illegal liquor", 4.8),
        ("sarayam", 4.8), ("kavalthurai", 5.0), ("போலீஸ்", 5.0), ("காவல்துறை", 5.0),
        ("திருடன்", 5.0), ("திருட்டு", 5.0), ("விபத்து", 5.0), ("கொலை", 5.5), ("கொள்ளை", 5.5),
        ("அடிதடி", 5.0), ("தாக்குதல்", 5.0), ("பாதுகாப்பு இல்லை", 5.0), ("அவசர உதவி", 5.0),
        ("பயமா இருக்கு", 4.5), ("காவல் நிலையம்", 5.0), ("ரோந்து வாகனம்", 5.0),
        
        # Core root stems
        ("police", 4.0), ("crime", 4.0), ("போலீஸ்", 4.0), ("thiruttu", 4.0), ("sanda", 3.8),
        ("accident", 4.0), ("விபத்து", 4.0), ("விபத்துக்கள்", 4.0), ("threat", 3.5), ("100", 4.0)
    ],
    "Water": [
        # Drinking water, pipeline & supply disruptions
        ("drinking water", 5.0), ("water supply", 5.0), ("pipe burst", 5.0), ("pipeline burst", 5.0),
        ("pipe leak", 4.8), ("pipeline leak", 4.8), ("water leak", 4.8), ("leak aaguthu", 4.2),
        ("thanni varala", 5.0), ("thanni varale", 5.0), ("thanniye varala", 5.0), ("thanniyilla", 5.0),
        ("kudineer varala", 5.0), ("kudineer illa", 5.0), ("kudineerilla", 5.0), ("no water", 5.0),
        ("water cut", 5.0), ("water shortage", 4.5), ("low pressure", 4.2), ("pressure illa", 4.2),
        ("pressure kammi", 4.2), ("water tanker", 4.5), ("tanker thanni", 4.5), ("borewell", 4.5),
        ("motor pump", 4.2), ("motor fault", 4.0), ("metro water", 5.0), ("cmwssb", 5.0), ("twad", 5.0),
        ("thanni waste", 4.2), ("water wastage", 4.2), ("water contamination", 5.0), ("yellow water", 4.5),
        ("dirty water", 4.5), ("smelly water", 4.5), ("drinking pipe", 4.5), ("sump fill", 4.0),
        ("pipe la sewage", 5.0), ("thanni karuppa", 4.8), ("thannila puzhu", 4.8), ("thanniyila puzhu", 4.8),
        ("kuzhai odanju", 4.8), ("kuzhai udaipu", 4.8), ("kuzhai kaisvu", 4.8), ("tap broken", 4.2),
        ("sintex tank", 4.2), ("handpump", 4.2), ("water problem", 4.0), ("thanni problem", 4.5),
        ("kuzhai உடைப்பு", 5.0), ("குழாய் உடைப்பு", 5.0), ("குழாய் கசிவு", 5.0), ("குடிநீர் வரவில்லை", 5.0),
        ("தண்ணீர் வரவில்லை", 5.0), ("நீர் விநியோகம்", 4.5), ("குடிநீர் தட்டுப்பாடு", 5.0), ("நீர் தட்டுப்பாடு", 5.0),
        ("கலங்கலான நீர்", 4.8), ("மஞ்சள் நிற தண்ணீர்", 4.8), ("குடிநீர் தொட்டி", 4.5), ("குடிநீர் குழாய்", 5.0),

        # Core root stems / keywords
        ("kudineer", 3.8), ("குடிநீர்", 3.8), ("thanni", 3.5), ("thanneer", 3.5), ("தண்ணீர்", 3.5),
        ("pipeline", 3.2), ("pipe", 2.8), ("குழாய்", 3.2), ("kuzhai", 3.2), ("borewell", 3.5),
        ("sump", 3.0), ("tanker", 3.0), ("போர்வெல்", 3.5), ("மோட்டார்", 3.0), ("வாட்டர்லைன்", 3.8)
    ],
    "Electricity": [
        # Power outages, lines, transformers, meters & lighting
        ("power cut", 5.0), ("current cut", 5.0), ("current cut aagi", 5.0), ("current cut aaiduchi", 5.0),
        ("current illa", 5.0), ("currentila", 5.0), ("power illa", 5.0), ("powerilla", 5.0),
        ("no power", 5.0), ("power supply", 5.0), ("power outage", 5.0), ("blackout", 5.0),
        ("live wire", 5.2), ("wire arunthu", 5.2), ("wire thonguthu", 4.8), ("wire arnchu", 4.8),
        ("spark adikuthu", 4.8), ("sparking", 4.8), ("transformer spark", 5.2), ("transformer blast", 5.2),
        ("electric shock", 5.2), ("shock adikuthu", 4.8), ("current shock", 5.0), ("street light", 4.5),
        ("streetlight", 4.5), ("streetlights", 4.5), ("light eriyala", 4.5), ("light podala", 4.5),
        ("theru light", 4.5), ("theru vilakku", 4.8), ("light fault", 4.2), ("fuse pochu", 4.5),
        ("low voltage", 4.5), ("high voltage", 4.5), ("voltage problem", 4.2), ("short circuit", 4.8),
        ("electric pole", 4.5), ("eb meter", 4.5), ("meter box", 4.5), ("electric meter", 4.5),
        ("meter board", 4.5), ("eb bill", 4.2), ("excess bill", 4.0), ("current bill", 4.2),
        ("light poiduchu", 4.2), ("not glowing", 4.2), ("மின் தடை", 5.0), ("மின் கம்பி", 5.0),
        ("மின் கம்பம்", 5.0), ("தெரு விளக்கு", 5.0), ("தெருவிளக்கு", 5.0), ("மின்விளக்கு", 4.5),
        ("மின்சார அதிர்ச்சி", 5.2), ("பவர் கட்", 5.0), ("குறைந்த மின்னழுத்தம்", 4.5), ("மின் கசிவு", 4.8),
        ("மின்சார கம்பி", 5.2), ("மின் மீட்டர்", 4.5), ("கரண்ட் இல்லை", 5.0),

        # Core root stems / keywords
        ("tangedco", 4.2), ("tneb", 4.2), ("டிஎன்பி", 4.2), ("மின்சாரம்", 4.0), ("electricity", 4.0),
        ("current", 3.8), ("கரண்ட்", 3.8), ("karand", 3.8), ("karantu", 3.8), ("transformer", 3.8),
        ("டிரான்ஸ்பார்மர்", 3.8), ("voltage", 3.5), ("வோல்டேஜ்", 3.5), ("streetlight", 3.8),
        ("wire", 3.0), ("fuse", 3.2), ("பியூஸ்", 3.2), ("kambam", 3.0), ("eb", 3.0), ("மின்", 2.8)
    ],
    "Roads": [
        # Potholes, damaged roads, bridges, bus stops & road cuts
        ("pothole", 5.0), ("potholes", 5.0), ("crater", 4.5), ("craters", 4.5), ("gundu kuzhi", 5.0),
        ("gundukuzhi", 5.0), ("broken road", 5.0), ("damaged road", 5.0), ("damaged street", 4.5),
        ("tar road", 4.5), ("cement road", 4.5), ("speed breaker", 4.5), ("speedbreaker", 4.5),
        ("road repair", 4.8), ("traffic hazard", 4.5), ("cave-in", 4.8), ("road damage", 5.0),
        ("road full damage", 5.0), ("road seri illa", 4.5), ("saalai mosam", 4.5), ("vandi poga mudila", 4.2),
        ("nadakka mudila", 4.0), ("flyover", 4.2), ("bridge damaged", 4.8), ("footpath", 4.0),
        ("pedestrian", 3.8), ("pavement", 3.8), ("asphalt", 4.0), ("highway hazard", 4.5),
        ("road fulla", 3.8), ("cement udrinju", 4.2), ("bus stop", 4.2), ("bus stand", 4.2),
        ("bus shelter", 4.2), ("பேருந்து நிறுத்தம்", 4.5), ("traffic signal", 4.5), ("road dug", 4.8),
        ("pipe dug and road", 5.0), ("road cut", 4.8), ("road thondi", 4.8), ("குண்டும் குழியும்", 5.0),
        ("சாலை சேதம்", 5.0), ("தார் சாலை", 4.5), ("சிமெண்ட் சாலை", 4.5), ("வேகத்தடை", 4.5),
        ("மேம்பாலம்", 4.2), ("நடைபாதை", 4.0),

        # Core root stems / keywords
        ("pothole", 4.2), ("pallam", 3.8), ("பள்ளம்", 3.8), ("kuzhi", 3.5), ("குழி", 3.5),
        ("speedbreaker", 3.8), ("bridge", 3.2), ("பாலம்", 3.2), ("highway", 3.2), ("நெடுஞ்சாலை", 3.2),
        ("road", 2.8), ("சாலை", 2.8), ("ரோடு", 2.8), ("traffic", 2.8), ("போக்குவரத்து", 2.8)
    ],
    "Sanitation": [
        # Drainage, sewage, garbage, public toilets, manholes, vectors
        ("drainage block", 5.0), ("drain block", 5.0), ("sewage overflow", 5.0), ("saakadai adaippu", 5.0),
        ("saakadai overflow", 5.0), ("drainage overflow", 5.0), ("kuppai allala", 5.0), ("kuppai thotti", 4.8),
        ("waste pile", 4.5), ("overflowing bin", 4.8), ("garbage overflow", 5.0), ("foul smell", 4.5),
        ("bad odor", 4.5), ("naatham adikuthu", 4.8), ("smell adikuthu", 4.5), ("sewer overflow", 5.0),
        ("sewage entering", 5.0), ("clean pannala", 4.2), ("cleaning team", 4.2), ("bleaching powder", 4.5),
        ("kosu thollai", 4.5), ("mosquito problem", 4.5), ("dead animal", 4.8), ("dead dog", 4.8),
        ("sanitary worker", 4.2), ("public toilet", 5.0), ("kazhivarai", 5.0), ("கழிப்பறை", 5.0),
        ("கழிவறை", 5.0), ("manhole cover", 5.0), ("open manhole", 5.2), ("manhole moody", 5.0),
        ("manhole", 4.8), ("pathala saakadai", 5.0), ("underground drainage", 5.0), ("dirty and not cleaned", 4.5),
        ("asudhama irukku", 4.5), ("asutham", 4.2), ("கழிவுநீர் அடைப்பு", 5.0), ("சாக்கடை அடைப்பு", 5.0),
        ("சாக்கடை பொங்குதல்", 5.0), ("குப்பை தொட்டி", 4.8), ("குப்பை அள்ளவில்லை", 5.0), ("துர்நாற்றம்", 4.5),
        ("கொசு தொல்லை", 4.5), ("சாக்கடை நீர்", 4.8), ("கழிவு மேலாண்மை", 4.5),

        # Core root stems / keywords
        ("drainage", 4.0), ("sewage", 4.0), ("சாக்கடை", 4.0), ("saakadai", 4.0), ("sakadai", 4.0),
        ("garbage", 3.8), ("kuppai", 3.8), ("kuppa", 3.8), ("குப்பை", 3.8), ("trash", 3.5),
        ("gutter", 3.5), ("sewer", 3.8), ("துப்புரவு", 3.8), ("sanitation", 3.8), ("toilet", 3.8),
        ("naatham", 3.5), ("odor", 3.2), ("stink", 3.2), ("kosu", 3.2), ("mosquito", 3.2),
        ("கொசு", 3.2), ("கழிவுநீர்", 3.8), ("dustbin", 3.2), ("சுத்தம்", 2.8)
    ],
    "Other": [
        # Natural disasters, floods, trees, animals, revenue, documents, noise, parks
        ("fallen tree", 5.0), ("tree fallen", 5.0), ("maram vilundhu", 5.0), ("maram saanju", 5.0),
        ("kombu odanju", 4.5), ("branch broken", 4.5), ("maram killa", 4.5), ("heavy flood", 5.2),
        ("flood water", 5.0), ("water logged", 5.0), ("water logging", 5.0), ("water stagnant", 5.0),
        ("rain water stagnant", 5.0), ("rain flood", 5.0), ("mazhai vellam", 5.0), ("cyclone damage", 5.0),
        ("cyclone wind", 4.8), ("storm damage", 5.0), ("heavy rain flood", 5.2), ("encroachment", 4.5),
        ("aakramippu", 4.5), ("land dispute", 4.2), ("ration card", 4.5), ("ration shop", 4.5),
        ("ration rice", 4.5), ("patta", 4.2), ("chitta", 4.2), ("aadhaar", 4.0), ("aadhar card", 4.2),
        ("voter id", 4.0), ("collectorate", 4.2), ("taluk office", 4.2), ("stray dog", 4.5),
        ("street dog", 4.5), ("dog menace", 4.5), ("dogs biting", 4.8), ("naai kootam", 4.5),
        ("theru naai", 4.5), ("naainga kadikka", 4.8), ("noise pollution", 4.5), ("loudspeaker", 4.5),
        ("sound pollution", 4.5), ("building collapse", 5.0), ("public park", 4.5), ("poonga maintenance", 4.5),
        ("poonga", 4.2), ("காய்ந்த மரம்", 5.0), ("மரம் விழுந்து", 5.0), ("மரக்கிளை", 4.5),
        ("வெள்ளம்", 5.0), ("புயல்", 5.0), ("மழை நீர் தேக்கம்", 5.0), ("பட்டா", 4.2), ("சிட்டா", 4.2),
        ("ஆக்கிரமிப்பு", 4.5), ("ரேஷன் கடை", 4.5), ("ரேஷன் அரிசி", 4.5), ("தெரு நாய்", 4.5),
        ("ஒலி மாசு", 4.5), ("பூங்கா", 4.2), ("கலெக்டர் அலுவலகம்", 4.2),

        # Core root stems / keywords
        ("maram", 3.2), ("tree", 3.0), ("மரம்", 3.2), ("disaster", 3.8), ("பேரிடர்", 3.8),
        ("flood", 4.0), ("vellam", 4.0), ("revenue", 3.2), ("வருவாய்", 3.2), ("encroach", 3.8),
        ("ration", 3.5), ("ரேஷன்", 3.5), ("naai", 3.2), ("dog", 3.0), ("நாய்கள்", 3.2),
        ("park", 3.0), ("பூங்கா", 3.2), ("aadhaar", 3.2), ("patta", 3.2)
    ]
}

# Preposition/Location words that should NOT override the root problem
LOCATION_PREPOSITIONS = {
    "road la", "roadla", "roadle", "rottula", "rottule", "roadula",
    "street la", "streetla", "therula", "theruvula", "theruvil", "area la", "areala",
    "oorla", "veetla", "veetula", "nagar la", "nagarla", "junction la", "gate la"
}

# High-priority and emergency keywords
EMERGENCY_TRIGGERS = [
    "live wire", "wire arunthu", "wire arnchu", "spark", "thee", "neruppu", "theepidithu",
    "vedichiduchu", "blast", "explosion", "shock adikuthu", "electric shock", "uyirukku aabathu",
    "uyir aabathu", "emergency", "immediate danger", "avasaram", "periya accident",
    "fatal accident", "open manhole", "manhole thirandhirukku", "sewage inside house",
    "veetukulla saakadai", "water poison", "toxic", "building collapse", "drowning risk",
    "severe water contamination", "life threatening"
]

HIGH_PRIORITY_TRIGGERS = [
    "3 days", "3 naal", "3 naala", "4 days", "4 naal", "5 days", "one week", "1 week",
    "oru vaaram", "continuous", "hospital", "school", "maruthuvamanai", "palli",
    "entire street", "mulu theru", "area fulla", "no water for days", "power cut continuously",
    "pipeline burst", "burst pipe", "sewage overflow", "deep hole", "deep crater"
]

# Tamil Nadu localities & Tamil Unicode district mapping
TAMIL_DISTRICT_MAP = {
    "சென்னை": "Chennai", "செங்கல்பட்டு": "Chengalpattu", "திருவள்ளூர்": "Tiruvallur",
    "காஞ்சிபுரம்": "Kanchipuram", "வேலூர்": "Vellore", "ராணிப்பேட்டை": "Ranipet",
    "திருப்பத்தூர்": "Tirupathur", "திருவண்ணாமலை": "Tiruvannamalai", "விழுப்புரம்": "Viluppuram",
    "கள்ளக்குறிச்சி": "Kallakurichi", "கடலூர்": "Cuddalore", "சேலம்": "Salem",
    "நாமக்கல்": "Namakkal", "தர்மபுரி": "Dharmapuri", "கிருஷ்ணகிரி": "Krishnagiri",
    "ஈரோடு": "Erode", "திருப்பூர்": "Tiruppur", "கோயம்புத்தூர்": "Coimbatore",
    "கோவை": "Coimbatore", "நீலகிரி": "Nilgiris", "கரூர்": "Karur",
    "திருச்சிராப்பள்ளி": "Tiruchirappalli", "திருச்சி": "Tiruchirappalli",
    "பெரம்பலூர்": "Perambalur", "அரியலூர்": "Ariyalur", "தஞ்சாவூர்": "Thanjavur",
    "திருவாரூர்": "Tiruvarur", "நாகப்பட்டினம்": "Nagapattinam", "மயிலாடுதுறை": "Mayiladuthurai",
    "புதுக்கோட்டை": "Pudukkottai", "திண்டுக்கல்": "Dindigul", "தேனி": "Theni",
    "மதுரை": "Madurai", "விருதுநகர்": "Virudhunagar", "சிவகங்கை": "Sivaganga",
    "ராமநாதபுரம்": "Ramanathapuram", "தூத்துக்குடி": "Thoothukudi", "திருநெல்வேலி": "Tirunelveli",
    "தென்காசி": "Tenkasi", "கன்னியாகுமரி": "Kanyakumari"
}

LOCALITY_MAP = {
    "anna nagar": "Chennai", "t. nagar": "Chennai", "t nagar": "Chennai", "velachery": "Chennai",
    "tambaram": "Chengalpattu", "adyar": "Chennai", "mylapore": "Chennai", "guindy": "Chennai",
    "chromepet": "Chengalpattu", "porur": "Chennai", "ambattur": "Chennai", "avadi": "Tiruvallur",
    "gandhipuram": "Coimbatore", "rs puram": "Coimbatore", "peelamedu": "Coimbatore",
    "saravanampatti": "Coimbatore", "singanallur": "Coimbatore", "goripalayam": "Madurai",
    "mattuthavani": "Madurai", "simmakkal": "Madurai", "thillai nagar": "Tiruchirappalli",
    "srirangam": "Tiruchirappalli", "k.k. nagar": "Tiruchirappalli", "hastampatti": "Salem",
    "fairlands": "Salem", "suramangalam": "Salem", "palayamkottai": "Tirunelveli",
    "vannarpettai": "Tirunelveli", "thirunagar": "Madurai", "katpadi": "Vellore",
    "gandhi nagar": "Vellore"
}


class NLPClassifier:
    """Classifies citizen complaints into Category, Priority, Department, and extracts entities."""

    def __init__(self):
        self.categories = CATEGORIES
        self.priorities = PRIORITY_LEVELS

    def extract_district(self, text: str, explicit_district: Optional[str] = None) -> Optional[str]:
        """Identifies Tamil Nadu district from explicit parameter or message text."""
        if explicit_district and explicit_district.strip() and explicit_district.strip() != "Select District":
            for d in TAMIL_NADU_DISTRICTS:
                if d.lower() == explicit_district.strip().lower():
                    return d
            return explicit_district.strip().title()

        text_lower = text.lower() if text else ""

        # Check Tamil Unicode district names
        for ta_name, dist_en in TAMIL_DISTRICT_MAP.items():
            if ta_name in text:
                return dist_en

        # Check locality names first
        for locality, district in LOCALITY_MAP.items():
            if re.search(r"\b" + re.escape(locality) + r"\b", text_lower):
                return district

        # Check district names
        for district in TAMIL_NADU_DISTRICTS:
            if re.search(r"\b" + re.escape(district.lower()) + r"\b", text_lower):
                return district

        return None

    def classify_category(self, text: str, detected_language: str = "tanglish") -> Tuple[str, float, List[str]]:
        """
        Robust category classifier supporting Tamil Unicode, agglutinated Tanglish, and English.
        """
        if not text or not text.strip():
            return "Other", 0.70, []

        clean_text = text.lower().strip()
        scores: Dict[str, float] = {cat: 0.0 for cat in self.categories}
        matched_words: Dict[str, List[str]] = {cat: [] for cat in self.categories}

        # Check all category patterns
        for cat, patterns in CATEGORY_PATTERNS.items():
            for pattern_text, weight in patterns:
                p_lower = pattern_text.lower()
                
                # Use word-boundary check for short ASCII tokens (e.g., "tree" should NOT match "street")
                is_short_ascii = p_lower.isalpha() and p_lower.isascii() and len(p_lower) <= 4
                if is_short_ascii:
                    is_match = bool(re.search(r"\b" + re.escape(p_lower) + r"\b", clean_text))
                else:
                    is_match = (p_lower in clean_text)

                if is_match:
                    # Penalize if it is merely a spatial location preposition (e.g. "road la")
                    if p_lower in LOCATION_PREPOSITIONS and cat == "Roads":
                        final_weight = weight * 0.4
                    else:
                        final_weight = weight

                    scores[cat] += final_weight
                    matched_words[cat].append(pattern_text)

        # Contextual tie-breaker:
        # 1. Flood / Storm / Rain water logging is Disaster Redressal (Other), NOT Drinking Water (Water)
        if any(w in clean_text for w in ["flood", "water logged", "water logging", "water stagnant", "rain water", "vellam", "mazhai vellam", "cyclone", "storm", "theki kidakuthu"]):
            scores["Other"] += 4.0
            scores["Water"] = max(0.0, scores["Water"] - 5.0)

        # 2. Road digging / cuts / damage / bus stops should prioritize Roads over Water
        if any(w in clean_text for w in ["pipe dug and road", "pipe dug", "road dug", "road cut", "road thondi", "road keduthu", "bus stand", "bus stop", "bus shelter"]):
            scores["Roads"] += 3.5
            scores["Water"] = max(0.0, scores["Water"] - 3.0)

        # 3. Manholes / Public toilets / sewage on road belongs to Sanitation, NOT Roads
        if any(w in clean_text for w in ["manhole", "open manhole", "toilet", "kazhivarai", "pathala saakadai", "underground drainage"]):
            scores["Sanitation"] += 3.5
            scores["Roads"] = max(0.0, scores["Roads"] - 3.0)

        # 4. If "kuppai" or "saakadai" is present on a "road", Sanitation wins over Roads
        if any(w in clean_text for w in ["kuppai", "kuppa", "garbage", "trash", "saakadai", "drainage", "sewage"]):
            scores["Sanitation"] += 2.0
            scores["Roads"] = max(0.0, scores["Roads"] - 2.0)

        # 5. If "pipe" / "pipeline" or "thanni" / "kudineer" is on a "road" (and not road digging/flood), Water wins over Roads
        if any(w in clean_text for w in ["pipe leak", "pipeline leak", "pipe burst", "pipeline burst", "thanni", "kudineer", "drinking"]):
            scores["Water"] += 2.0
            scores["Roads"] = max(0.0, scores["Roads"] - 2.0)

        # 6. If "wire" / "current" / "light" / "spark" is on a "road", Electricity wins over Roads
        if any(w in clean_text for w in ["wire", "current", "spark", "light", "transformer", "pole", "kambam", "vilakku"]):
            scores["Electricity"] += 2.0
            scores["Roads"] = max(0.0, scores["Roads"] - 2.0)

        # Find best matching category
        best_cat = "Other"
        max_score = 0.0
        for cat, score in scores.items():
            if score > max_score:
                max_score = score
                best_cat = cat

        if max_score < 1.0:
            return "Other", 0.70, []

        confidence = min(0.99, 0.75 + (max_score * 0.05))
        return best_cat, round(confidence, 2), list(set(matched_words[best_cat]))

    def detect_priority(self, text: str, category: str) -> Tuple[str, Optional[str]]:
        """
        Detects urgency level: Emergency, High, Medium, or Low.
        """
        text_lower = text.lower() if text else ""

        # 1. Emergency check
        for trigger in EMERGENCY_TRIGGERS:
            if trigger in text_lower:
                return "Emergency", f"Triggered by safety hazard keyword: '{trigger}'"

        # 2. High priority check
        for trigger in HIGH_PRIORITY_TRIGGERS:
            if trigger in text_lower:
                return "High", f"Triggered by prolonged outage / community impact keyword: '{trigger}'"

        # 3. Category based standard defaults
        if category == "Police":
            if any(w in text_lower for w in ["murder", "kolai", "attack", "kidnap", "danger", "robbery", "kollai", "accident", "sanda", "threat"]):
                return "Emergency", "Immediate Police & Safety emergency intervention required"
            return "High", "Police Control Room / Public safety matter"
        elif category in ["Electricity", "Water"]:
            if any(w in text_lower for w in ["not working", "eriyala", "varala", "cut", "leak", "damage", "burst", "illa", "problem"]):
                return "High", "Active utility disruption reported"
            return "Medium", "Standard utility grievance"
        elif category in ["Sanitation", "Roads"]:
            if any(w in text_lower for w in ["overflow", "pothole", "accident", "smell", "block", "kuzhi", "naatham"]):
                return "Medium", "Public infrastructure / sanitation maintenance"
            return "Low", "Routine maintenance grievance"

        return "Low", "General administrative enquiry or minor grievance"

    def get_department_for_category(self, category: str) -> Dict[str, Any]:
        """Returns the corresponding Tamil Nadu government department metadata."""
        for dept in TAMIL_NADU_DEPARTMENTS:
            if dept["category"] == category:
                return dept
        return TAMIL_NADU_DEPARTMENTS[-1]

    def analyze(self, text: str, detected_language: str = "tanglish", explicit_district: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete AI analysis package for a given text.
        """
        category, confidence, matched_keywords = self.classify_category(text, detected_language)
        priority, urgency_reason = self.detect_priority(text, category)
        district = self.extract_district(text, explicit_district)
        dept_info = self.get_department_for_category(category)

        return {
            "category": category,
            "priority": priority,
            "confidence_score": confidence,
            "matched_keywords": matched_keywords,
            "urgency_reason": urgency_reason,
            "extracted_district": district,
            "department_code": dept_info["code"],
            "department_name_en": dept_info["name_en"],
            "department_name_ta": dept_info["name_ta"],
            "department_helpline": dept_info["helpline_number"]
        }


nlp_classifier = NLPClassifier()
