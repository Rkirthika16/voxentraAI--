import os
import uuid
import logging
import requests
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.config import settings, UPLOAD_DIR
from app.services.complaint_service import complaint_service
from app.utils.audio_utils import create_synthetic_test_wav

logger = logging.getLogger("voxentra.services.telephony")

class TelephonyService:
    """Manages Voice IVR flows, TwiML responses, and voice call recording ingestion."""

    @staticmethod
    def generate_incoming_call_twiml(action_url: str) -> str:
        """
        Generates TwiML XML greeting for incoming voice calls.
        Greets the citizen in Tamil and English, and initiates recording.
        """
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="ta-IN" voice="Polly.Valluvar">வணக்கம். தமிழ்நாடு அரசு குறைதீர்ப்பு சேவைக்கு வரவேற்கிறோம்.</Say>
    <Say language="en-IN" voice="Polly.Aditi">Welcome to Tamil Nadu Public Grievance Helpline. Please describe your complaint in Tamil, English, or Tanglish after the beep. Press hash when finished.</Say>
    <Record 
        action="{action_url}"
        method="POST"
        maxLength="120"
        finishOnKey="#"
        playBeep="true"
        recordingStatusCallback="{action_url}"
    />
    <Say language="ta-IN">உங்கள் குறையை பதிவு செய்ய முடியவில்லை. மீண்டும் அழைக்கவும்.</Say>
</Response>"""
        return twiml

    @staticmethod
    def generate_recording_confirmation_twiml(
        complaint_id: str,
        category: str,
        department_name: str = "Tamil Nadu Government",
        language: str = "tamil"
    ) -> str:
        """
        Generates dynamic TwiML confirmation speaking the generated Ticket ID to the citizen in their language.
        """
        from app.config import CATEGORY_DISPLAY
        digits_spoken = " ".join(list(complaint_id.replace("-", " ")))
        
        # Category localized display
        cat_info = CATEGORY_DISPLAY.get(category, {})
        cat_tamil = cat_info.get("ta", category)
        cat_english = cat_info.get("en", category)

        if category == "Police":
            if language in ["tamil", "ta"]:
                twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="ta-IN" voice="Polly.Valluvar">வணக்கம். தமிழ்நாடு காவல் மற்றும் அவசர கட்டுப்பாட்டு அறை. உங்கள் அவசர புகார் எண் {digits_spoken} பதிவு செய்யப்பட்டது. உங்கள் பகுதிக்கு அருகிலுள்ள காவல் ரோந்து வாகனத்திற்கும் அதிகாரிகளுக்கும் அவசர தகவல் அனுப்பப்பட்டுள்ளது. அதிகாரிகள் உடனடியாக நடவடிக்கை எடுப்பார்கள். பதற வேண்டாம், பாதுகாப்பான இடத்தில் இருங்கள்.</Say>
    <Hangup/>
</Response>"""
            else:
                twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="en-IN" voice="Polly.Aditi">Tamil Nadu Police and Emergency Control Room (100/112). Your emergency ticket {digits_spoken} has been registered with high priority. Patrol units and local police have been alerted for immediate response. Please stay calm and remain in a safe location.</Say>
    <Hangup/>
</Response>"""
            return twiml

        elif category == "Electricity":
            if language in ["tamil", "ta"]:
                twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="ta-IN" voice="Polly.Valluvar">வணக்கம். தமிழ்நாடு மின்சார வாரியம் மற்றும் மின் உற்பத்தி பகிர்மானக் கழகம். உங்கள் மின்சார புகார் எண் {digits_spoken} பதிவு செய்யப்பட்டது. உங்கள் பகுதி உதவி பொறியாளர் மற்றும் லைன் ஆய்வாளருக்கு உடனடி நடவடிக்கைக்காக அனுப்பப்பட்டுள்ளது. அறுந்து கிடக்கும் மின்கம்பிகள் அருகே செல்ல வேண்டாம். உதவி எண் 1912.</Say>
    <Hangup/>
</Response>"""
            else:
                twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="en-IN" voice="Polly.Aditi">Tamil Nadu Generation and Distribution Corporation (TANGEDCO Electricity Helpline 1912). Your electricity grievance {digits_spoken} has been registered. Zonal line inspector and maintenance engineers have been dispatched for prompt power restoration. Please stay clear of open electric cables.</Say>
    <Hangup/>
</Response>"""
            return twiml

        elif category == "Water":
            if language in ["tamil", "ta"]:
                twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="ta-IN" voice="Polly.Valluvar">வணக்கம். தமிழ்நாடு குடிநீர் வழங்கல் மற்றும் கழிவுநீரகற்று வாரியம். உங்கள் குடிநீர் புகார் எண் {digits_spoken} பதிவு செய்யப்பட்டது. உங்கள் வார்டு உதவி பொறியாளர் மற்றும் குழாய் சீரமைப்பு குழுவிற்கு தகவல் அனுப்பப்பட்டு உடனடி நடவடிக்கை எடுக்கப்பட்டுள்ளது. உதவி எண் 1916.</Say>
    <Hangup/>
</Response>"""
            else:
                twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="en-IN" voice="Polly.Aditi">Tamil Nadu Water Supply and Drainage Board (TWAD / Metro Water Helpline 1916). Your water supply complaint {digits_spoken} is registered. Zonal water distribution engineers and pipeline maintenance crew have been alerted for inspection and repair.</Say>
    <Hangup/>
</Response>"""
            return twiml

        elif category == "Roads":
            if language in ["tamil", "ta"]:
                twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="ta-IN" voice="Polly.Valluvar">வணக்கம். தமிழ்நாடு நெடுஞ்சாலைகள் மற்றும் மாநகராட்சி சாலைகள் துறை. உங்கள் சாலை சேத புகார் எண் {digits_spoken} பதிவு செய்யப்பட்டது. நெடுஞ்சாலை உதவி பொறியாளர் மற்றும் சாலை சீரமைப்பு பணிக்குழுவிற்கு தகவல் அனுப்பப்பட்டுள்ளது.</Say>
    <Hangup/>
</Response>"""
            else:
                twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="en-IN" voice="Polly.Aditi">Highways Department and Corporation Roads Wing. Your road infrastructure ticket {digits_spoken} is registered. Field engineering team and road repair crew have been assigned to inspect and rectify the damage.</Say>
    <Hangup/>
</Response>"""
            return twiml

        elif category == "Sanitation":
            if language in ["tamil", "ta"]:
                twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="ta-IN" voice="Polly.Valluvar">வணக்கம். நகராட்சி நிர்வாகம் மற்றும் பொது சுகாதாரத் துறை. உங்கள் தூய்மை மற்றும் கழிவுநீர் புகார் எண் {digits_spoken} பதிவு செய்யப்பட்டது. உங்கள் பகுதி துப்புரவு ஆய்வாளர் மற்றும் தூய்மைப் பணியாளர்களுக்கு உடனடி நடவடிக்கைக்காக அனுப்பப்பட்டுள்ளது. உதவி எண் 1913.</Say>
    <Hangup/>
</Response>"""
            else:
                twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="en-IN" voice="Polly.Aditi">Municipal Administration and Public Health Department (Helpline 1913). Your sanitation and drain clearance grievance {digits_spoken} is registered. Zonal sanitary inspector and ground cleaning team dispatched for immediate action.</Say>
    <Hangup/>
</Response>"""
            return twiml

        elif category in ["Other", "Revenue"]:
            if language in ["tamil", "ta"]:
                twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="ta-IN" voice="Polly.Valluvar">வணக்கம். மாவட்ட ஆட்சியர் அலுவலகம் மற்றும் பேரிடர் மேலாண்மை கட்டுப்பாட்டு அறை. உங்கள் புகார் எண் {digits_spoken} பதிவு செய்யப்பட்டு வட்டாட்சியர் மற்றும் வருவாய்த்துறை அதிகாரிகளுக்கு அனுப்பப்பட்டுள்ளது. உதவி எண் 1077.</Say>
    <Hangup/>
</Response>"""
            else:
                twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="en-IN" voice="Polly.Aditi">Revenue and Disaster Management Control Desk (Helpline 1077). Grievance ticket {digits_spoken} registered and assigned to District Collectorate and Taluk Revenue officials for resolution.</Say>
    <Hangup/>
</Response>"""
            return twiml

        if language in ["tamil", "ta"]:
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="ta-IN" voice="Polly.Valluvar">வணக்கம். உங்கள் புகார் எண் {digits_spoken} வெற்றிகரமாக பதிவு செய்யப்பட்டது. உங்கள் {cat_tamil} குறை சம்பந்தப்பட்ட {department_name} துறைக்கு உடனடியாக அனுப்பப்பட்டுள்ளது. உங்கள் மொபைல் எண்ணிற்கு எஸ்எம்எஸ் அனுப்பப்பட்டுள்ளது. தமிழ்நாடு அரசு உதவி மையத்தை தொடர்பு கொண்டதற்கு நன்றி.</Say>
    <Hangup/>
</Response>"""
        else:
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="en-IN" voice="Polly.Aditi">Thank you. Your grievance has been registered under ticket {digits_spoken}. Your {cat_english} issue has been assigned to {department_name}. An SMS confirmation with your live tracking link has been sent to your mobile number. Thank you for calling Government of Tamil Nadu helpline.</Say>
    <Hangup/>
</Response>"""
        return twiml

    @classmethod
    def process_call_recording(
        cls,
        db: Session,
        caller_phone: str,
        recording_url: Optional[str] = None,
        local_audio_path: Optional[str] = None,
        transcription_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Downloads / retrieves audio recording, runs speech AI, and creates complaint.
        """
        final_audio_path = local_audio_path

        # If remote recording URL provided from Twilio, download it
        if recording_url and not final_audio_path:
            try:
                import uuid
                local_filename = f"call_{uuid.uuid4().hex[:10]}.wav"
                target_file = UPLOAD_DIR / local_filename
                
                # Fetch audio file (Twilio, Exotel, or direct public S3 URL)
                auth = None
                if "twilio" in recording_url.lower() and not settings.TWILIO_MOCK_MODE:
                    auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                elif "exotel" in recording_url.lower() and settings.EXOTEL_API_KEY:
                    auth = (settings.EXOTEL_API_KEY, settings.EXOTEL_API_TOKEN)

                response = requests.get(recording_url, auth=auth, timeout=6)
                if response.status_code != 200 and auth is not None:
                    # Retry without auth in case it's a public pre-signed S3 URL
                    response = requests.get(recording_url, timeout=6)

                if response.status_code == 200:
                    with open(target_file, "wb") as f:
                        f.write(response.content)
                    final_audio_path = str(target_file)
                else:
                    logger.warning(f"Could not download recording from {recording_url}, status: {response.status_code}")
            except Exception as e:
                logger.error(f"Error fetching telephony audio recording: {e}")

        # Fallback to synthetic or sample audio if recording is simulated
        if not final_audio_path or not os.path.exists(final_audio_path):
            sample_file = UPLOAD_DIR / f"simulated_call_{caller_phone.replace('+', '')[-6:]}.wav"
            create_synthetic_test_wav(str(sample_file))
            final_audio_path = str(sample_file)

        # Create Complaint with transcription hint if provided
        complaint = complaint_service.create_voice_complaint(
            db=db,
            phone_number=caller_phone,
            audio_file_path=final_audio_path,
            channel="voice_call",
            explicit_message=transcription_hint
        )

        return {
            "status": "success",
            "complaint_id": complaint.id,
            "category": complaint.category,
            "priority": complaint.priority,
            "transcription": complaint.transcribed_text,
            "language": complaint.language,
            "department": complaint.department_code,
            "audio_file": final_audio_path
        }

    @classmethod
    def initiate_outbound_call(
        cls,
        to_phone: str,
        custom_caller_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Triggers an outbound phone call to connect a citizen's mobile phone directly with the AI Agent.
        Uses Exotel REST API if configured, otherwise Twilio, or provides a simulated live session.
        """
        clean_phone = "".join(ch for ch in to_phone if ch.isdigit() or ch == "+")
        if len(clean_phone) == 10 and not clean_phone.startswith("+"):
            formatted_phone = f"+91{clean_phone}"
        elif len(clean_phone) == 12 and clean_phone.startswith("91"):
            formatted_phone = f"+{clean_phone}"
        else:
            formatted_phone = clean_phone

        caller_id = custom_caller_id or settings.EXOTEL_CALLER_ID or "08088919888"
        call_mode = "MOCK_SIMULATED"
        call_sid = f"call_{uuid.uuid4().hex[:12]}" if "uuid" in globals() else f"call_exo_{clean_phone[-6:]}"

        carrier_error = None

        # 1. Check Exotel credentials
        if (
            settings.EXOTEL_API_KEY
            and not settings.EXOTEL_API_KEY.startswith("your_")
            and not settings.EXOTEL_API_KEY.startswith("voxentra_")
            and settings.EXOTEL_API_TOKEN
            and settings.EXOTEL_ACCOUNT_SID
        ):
            try:
                exotel_call_url = f"https://api.exotel.com/v1/Accounts/{settings.EXOTEL_ACCOUNT_SID}/Calls/connect.json"
                auth = (settings.EXOTEL_API_KEY, settings.EXOTEL_API_TOKEN)
                payload = {
                    "From": formatted_phone,
                    "To": caller_id,
                    "CallerId": caller_id,
                    "Url": f"{settings.BASE_URL}/api/v1/webhooks/exotel/voice/incoming"
                }
                resp = requests.post(exotel_call_url, auth=auth, data=payload, timeout=10)
                if resp.status_code in (200, 201):
                    call_mode = "LIVE_EXOTEL_CARRIER"
                    call_data = resp.json().get("Call", {})
                    call_sid = call_data.get("Sid", call_sid)
                    logger.info(f"Live Exotel call connected to {formatted_phone} (Sid: {call_sid})")
                else:
                    carrier_error = f"Exotel HTTP {resp.status_code}: {resp.text}"
                    logger.warning(f"Exotel Call connect response: {resp.status_code} {resp.text}")
            except Exception as e:
                carrier_error = str(e)
                logger.error(f"Failed to initiate live Exotel call: {e}")

        # 2. Check Twilio credentials
        elif (
            settings.TWILIO_ACCOUNT_SID
            and not settings.TWILIO_ACCOUNT_SID.startswith("AC_dummy")
            and not settings.TWILIO_MOCK_MODE
        ):
            try:
                from twilio.rest import Client
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                call = client.calls.create(
                    to=formatted_phone,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    url=f"{settings.BASE_URL}/api/v1/webhooks/voice/incoming"
                )
                call_mode = "LIVE_TWILIO_CARRIER"
                call_sid = call.sid
                logger.info(f"Live Twilio call connected to {formatted_phone} (Sid: {call.sid})")
            except Exception as e:
                carrier_error = str(e)
                logger.error(f"Failed to initiate live Twilio call: {e}")

        msg = (
            f"Calling {formatted_phone} from {caller_id} ({call_mode}). Answer the call on your phone to talk with the AI."
            if call_mode != "MOCK_SIMULATED"
            else f"Telecom gateway fell back to simulated mode for {formatted_phone}."
        )

        return {
            "status": "initiated" if call_mode != "MOCK_SIMULATED" else "simulated",
            "to_phone": formatted_phone,
            "caller_id": caller_id,
            "call_sid": call_sid,
            "call_mode": call_mode,
            "carrier_error": carrier_error,
            "message": msg
        }

telephony_service = TelephonyService()
