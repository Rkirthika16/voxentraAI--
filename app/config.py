import os

from pathlib import Path
from typing import List, Dict, Tuple, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    APP_NAME: str = os.getenv("APP_NAME", "VoxentraAI")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1")
    API_PREFIX: str = os.getenv("API_PREFIX", "/api/v1")
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    BASE_URL: str = os.getenv("BASE_URL", "http://127.0.0.1:8000")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./voxentra.db")

    # AI & Speech-to-Text
    WHISPER_MODEL_SIZE: str = os.getenv("WHISPER_MODEL_SIZE", "base")
    WHISPER_DEVICE: str = os.getenv("WHISPER_DEVICE", "cpu")

    # Telephony & SMS (Twilio & Exotel)
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "AC_dummy_account_sid_voxentra")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "dummy_auth_token_voxentra")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "+914422334455")
    TWILIO_MOCK_MODE: bool = os.getenv("TWILIO_MOCK_MODE", "True").lower() in ("true", "1")

    EXOTEL_ACCOUNT_SID: str = os.getenv("EXOTEL_ACCOUNT_SID", "voxentra_exotel_sid")
    EXOTEL_API_KEY: str = os.getenv("EXOTEL_API_KEY", "voxentra_exotel_key")
    EXOTEL_API_TOKEN: str = os.getenv("EXOTEL_API_TOKEN", "voxentra_exotel_token")
    EXOTEL_CALLER_ID: str = os.getenv("EXOTEL_CALLER_ID", "08088919888")

    # Emergency Contacts in Tamil Nadu
    EMERGENCY_POLICE: str = os.getenv("EMERGENCY_POLICE", "100")
    EMERGENCY_AMBULANCE: str = os.getenv("EMERGENCY_AMBULANCE", "108")
    EMERGENCY_DISASTER: str = os.getenv("EMERGENCY_DISASTER", "1077")
    EMERGENCY_ELECTRICITY_TNEB: str = os.getenv("EMERGENCY_ELECTRICITY_TNEB", "1912")
    EMERGENCY_GCC_CHENNAI: str = os.getenv("EMERGENCY_GCC_CHENNAI", "1913")

settings = Settings()

# ==============================================================================
# Domain Constants for Tamil Nadu Public Grievance System
# ==============================================================================

CATEGORIES: List[str] = [
    "Police",
    "Water",
    "Electricity",
    "Roads",
    "Sanitation",
    "Other"
]

CATEGORY_DISPLAY: Dict[str, Dict[str, str]] = {
    "Police": {
        "en": "Police, Safety & Emergency Control (100)",
        "ta": "காவல்துறை மற்றும் அவசர கட்டுப்பாட்டு அறை (100)",
        "icon": "🚔",
        "code": "POL"
    },
    "Water": {
        "en": "Water Supply & Drainage",
        "ta": "குடிநீர் மற்றும் வடிகால்",
        "icon": "💧",
        "code": "WTR"
    },
    "Electricity": {
        "en": "Electricity & Power",
        "ta": "மின்சாரம் மற்றும் வெளிச்சம்",
        "icon": "⚡",
        "code": "ELE"
    },
    "Roads": {
        "en": "Roads & Traffic Infrastructure",
        "ta": "சாலைகள் மற்றும் போக்குவரத்து",
        "icon": "🛣️",
        "code": "ROA"
    },
    "Sanitation": {
        "en": "Sanitation, Garbage & Public Health",
        "ta": "துப்புரவு மற்றும் கழிவு மேலாண்மை",
        "icon": "🧹",
        "code": "SAN"
    },
    "Other": {
        "en": "General & Revenue Administration",
        "ta": "பொது மற்றும் பிற துறைகள்",
        "icon": "🏛️",
        "code": "OTH"
    }
}

PRIORITY_LEVELS: List[str] = [
    "Low",
    "Medium",
    "High",
    "Emergency"
]

STATUS_LEVELS: List[str] = [
    "Pending",
    "Under Review",
    "Assigned",
    "In Progress",
    "Resolved",
    "Rejected"
]

CHANNELS: List[str] = [
    "web_text",
    "voice_upload",
    "voice_call",
    "sms"
]

LANGUAGES: List[str] = [
    "tamil",
    "english",
    "tanglish"
]

TAMIL_NADU_DISTRICTS: List[str] = [
    "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore",
    "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kanchipuram",
    "Kanyakumari", "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai",
    "Nagapattinam", "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai",
    "Ramanathapuram", "Ranipet", "Salem", "Sivaganga", "Tenkasi",
    "Thanjavur", "Theni", "Thoothukudi", "Tiruchirappalli", "Tirunelveli",
    "Tirupathur", "Tiruppur", "Tiruvallur", "Tiruvannamalai", "Tiruvarur",
    "Vellore", "Viluppuram", "Virudhunagar"
]

TAMIL_NADU_DISTRICT_COORDS: Dict[str, Dict[str, float]] = {
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Chengalpattu": {"lat": 12.6841, "lon": 79.9836},
    "Tiruvallur": {"lat": 13.1432, "lon": 79.9079},
    "Kanchipuram": {"lat": 12.8342, "lon": 79.7036},
    "Ranipet": {"lat": 12.9272, "lon": 79.3330},
    "Vellore": {"lat": 12.9165, "lon": 79.1325},
    "Tirupathur": {"lat": 12.4926, "lon": 78.5678},
    "Krishnagiri": {"lat": 12.5186, "lon": 78.2137},
    "Dharmapuri": {"lat": 12.1211, "lon": 78.1582},
    "Tiruvannamalai": {"lat": 12.2253, "lon": 79.0747},
    "Viluppuram": {"lat": 11.9401, "lon": 79.4861},
    "Kallakurichi": {"lat": 11.7384, "lon": 78.9639},
    "Cuddalore": {"lat": 11.7480, "lon": 79.7714},
    "Salem": {"lat": 11.6643, "lon": 78.1460},
    "Namakkal": {"lat": 11.2189, "lon": 78.1674},
    "Erode": {"lat": 11.3410, "lon": 77.7172},
    "Nilgiris": {"lat": 11.4102, "lon": 76.6950},
    "Coimbatore": {"lat": 11.0168, "lon": 76.9558},
    "Tiruppur": {"lat": 11.1085, "lon": 77.3411},
    "Karur": {"lat": 10.9601, "lon": 78.0766},
    "Tiruchirappalli": {"lat": 10.7905, "lon": 78.7047},
    "Perambalur": {"lat": 11.2342, "lon": 78.8820},
    "Ariyalur": {"lat": 11.1401, "lon": 79.0782},
    "Mayiladuthurai": {"lat": 11.1018, "lon": 79.6522},
    "Nagapattinam": {"lat": 10.7672, "lon": 79.8449},
    "Tiruvarur": {"lat": 10.7725, "lon": 79.6365},
    "Thanjavur": {"lat": 10.7870, "lon": 79.1378},
    "Pudukkottai": {"lat": 10.3797, "lon": 78.8208},
    "Dindigul": {"lat": 10.3673, "lon": 77.9803},
    "Theni": {"lat": 10.0104, "lon": 77.4768},
    "Madurai": {"lat": 9.9252, "lon": 78.1198},
    "Sivaganga": {"lat": 9.8433, "lon": 78.4809},
    "Ramanathapuram": {"lat": 9.3639, "lon": 78.8395},
    "Virudhunagar": {"lat": 9.5680, "lon": 77.9624},
    "Tenkasi": {"lat": 8.9594, "lon": 77.3152},
    "Tirunelveli": {"lat": 8.7139, "lon": 77.7567},
    "Thoothukudi": {"lat": 8.7642, "lon": 78.1348},
    "Kanyakumari": {"lat": 8.0883, "lon": 77.5385}
}

def get_district_coordinates(district_name: Optional[str] = None) -> Tuple[float, float]:
    """Returns (latitude, longitude) for a Tamil Nadu district or state center default."""
    if district_name and district_name in TAMIL_NADU_DISTRICT_COORDS:
        coords = TAMIL_NADU_DISTRICT_COORDS[district_name]
        return coords["lat"], coords["lon"]
    # Default to center of Tamil Nadu (approx Tiruchirappalli)
    return 10.7905, 78.7047

TAMIL_NADU_DEPARTMENTS = [
    {
        "code": "TN_POLICE",
        "name_en": "Tamil Nadu Police & Emergency Control Room (100 / 112)",
        "name_ta": "தமிழ்நாடு காவல்துறை மற்றும் அவசர கட்டுப்பாட்டு அறை (100 / 112)",
        "category": "Police",
        "contact_email": "police.controlroom@tn.gov.in",
        "helpline_number": "100"
    },
    {
        "code": "TWAD_CMWSSB",
        "name_en": "Tamil Nadu Water Supply & Drainage Board / CMWSSB",
        "name_ta": "தமிழ்நாடு குடிநீர் வழங்கல் மற்றும் கழிவுநீரகற்று வாரியம்",
        "category": "Water",
        "contact_email": "water.grievance@tn.gov.in",
        "helpline_number": "1916"
    },
    {
        "code": "TANGEDCO",
        "name_en": "Tamil Nadu Generation and Distribution Corporation (TANGEDCO/TNEB)",
        "name_ta": "தமிழ்நாடு மின் உற்பத்தி மற்றும் பகிர்மானக் கழகம்",
        "category": "Electricity",
        "contact_email": "tneb.complaints@tn.gov.in",
        "helpline_number": "1912"
    },
    {
        "code": "HIGHWAYS_CORP",
        "name_en": "Highways Department & Corporation Roads Wing",
        "name_ta": "நெடுஞ்சாலைகள் மற்றும் மாநகராட்சி சாலைகள் துறை",
        "category": "Roads",
        "contact_email": "roads.support@tn.gov.in",
        "helpline_number": "1800-425-4357"
    },
    {
        "code": "SANITATION_HEALTH",
        "name_en": "Municipal Administration & Public Health Department",
        "name_ta": "நகராட்சி நிர்வாகம் மற்றும் பொது சுகாதாரத் துறை",
        "category": "Sanitation",
        "contact_email": "sanitation.clean@tn.gov.in",
        "helpline_number": "1913"
    },
    {
        "code": "REVENUE_DISASTER",
        "name_en": "Revenue & Disaster Management Department",
        "name_ta": "வருவாய் மற்றும் பேரிடர் மேலாண்மைத் துறை",
        "category": "Other",
        "contact_email": "collectorate.grievance@tn.gov.in",
        "helpline_number": "1077"
    }
]

if __name__ == "__main__":
    print("=" * 60)
    print(f"[CONFIG] {settings.APP_NAME} Configuration Loaded Successfully")
    print("=" * 60)
    print(f"- Environment:     {settings.APP_ENV}")
    print(f"- Database URL:    {settings.DATABASE_URL}")
    print(f"- API Host & Port: http://{settings.HOST}:{settings.PORT}")
    print(f"- API Prefix:      {settings.API_PREFIX}")
    print(f"- Twilio Mode:     {'MOCK MODE (Active)' if settings.TWILIO_MOCK_MODE else 'LIVE'}")
    print(f"- Categories:      {', '.join(CATEGORIES)}")
    print(f"- Districts:       {len(TAMIL_NADU_DISTRICTS)} Tamil Nadu Districts configured")
    print("=" * 60)
    print(">> To run the full application (FastAPI + Streamlit Portal):")
    print("   Run in terminal: python run.py")
    print("=" * 60)
