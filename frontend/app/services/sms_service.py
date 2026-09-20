import logging
import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.config import settings
from app.services.complaint_service import complaint_service
from app.schemas.complaint import ComplaintCreateText

logger = logging.getLogger("voxentra.services.sms")

# In-memory sent SMS records buffer for live citizen handset simulation and verification
SENT_SMS_LOG: List[Dict[str, Any]] = []


class SMSService:
    """Handles incoming SMS webhook processing and outbound SMS dispatch to citizens."""

    @staticmethod
    def format_phone_number(phone: str) -> str:
        """Standardizes 10-digit Indian phone numbers to E.164 format (+91...)."""
        clean = "".join(ch for ch in phone if ch.isdigit() or ch == "+")
        if clean.startswith("+91") and len(clean) == 13:
            return clean
        elif clean.startswith("91") and len(clean) == 12:
            return f"+{clean}"
        elif len(clean) == 10:
            return f"+91{clean}"
        return clean

    @staticmethod
    def generate_sms_reply_text(
        complaint_id: str,
        category: str,
        priority: str,
        department_name: str,
        language: str = "tamil"
    ) -> str:
        """
        Creates bilingual SMS confirmation response tailored to detected language.
        """
        if category == "Police":
            if language in ["tamil", "ta"]:
                return (
                    f"🚨 தமிழ்நாடு காவல் கட்டுப்பாட்டு அறை (100 / 112):\n"
                    f"அவசர புகார் எண்: {complaint_id}\n"
                    f"வகை: காவல்துறை மற்றும் அவசர உதவி ({priority})\n"
                    f"அருகிலுள்ள காவல் ரோந்து வாகனத்திற்கு தகவல் அனுப்பப்பட்டது.\n"
                    f"நேரடி கண்காணிப்பு: {settings.BASE_URL}/track/{complaint_id}\n"
                    f"காவல் உதவி எண்: 100 / 112 (24x7)"
                )
            elif language == "tanglish":
                return (
                    f"🚨 TN Police Emergency Control (100):\n"
                    f"Emergency Ticket ID: {complaint_id} registered.\n"
                    f"Category: Police & Safety ({priority})\n"
                    f"Patrol alert dispatched to nearest unit.\n"
                    f"Track live: {settings.BASE_URL}/track/{complaint_id}\n"
                    f"Emergency Helpline: 100 / 112"
                )
            else:
                return (
                    f"🚨 TN Police & Emergency Control (100 / 112):\n"
                    f"Emergency Ticket #{complaint_id} registered ({priority}).\n"
                    f"Patrol alert dispatched to nearest police response unit.\n"
                    f"Live Status Tracker: {settings.BASE_URL}/track/{complaint_id}\n"
                    f"Emergency Helpline: 100 / 112"
                )

        elif category == "Electricity":
            if language in ["tamil", "ta"]:
                return (
                    f"⚡ தமிழ்நாடு மின்சார வாரியம் (TANGEDCO 1912):\n"
                    f"மின் புகார் எண்: {complaint_id}\n"
                    f"முன்னுரிமை: {priority} | துறை: {department_name}\n"
                    f"லைன் ஆய்வாளர் மற்றும் பராமரிப்பு குழுவிற்கு அனுப்பப்பட்டுள்ளது.\n"
                    f"நேரடி கண்காணிப்பு: {settings.BASE_URL}/track/{complaint_id}\n"
                    f"மின் உதவி எண்: 1912 (24x7)"
                )
            elif language == "tanglish":
                return (
                    f"⚡ TANGEDCO Electricity Helpline 1912:\n"
                    f"Power Complaint #{complaint_id} registered ({priority}).\n"
                    f"Assigned: {department_name}\n"
                    f"Line maintenance crew dispatched for power restoration.\n"
                    f"Track live: {settings.BASE_URL}/track/{complaint_id}\n"
                    f"TNEB Helpline: 1912"
                )
            else:
                return (
                    f"⚡ TNEB TANGEDCO Electricity Control (1912):\n"
                    f"Grievance Ticket #{complaint_id} registered with {priority} priority.\n"
                    f"Assigned Department: {department_name}\n"
                    f"Live Status Tracker: {settings.BASE_URL}/track/{complaint_id}\n"
                    f"24x7 Power Helpline: 1912"
                )

        elif category == "Water":
            if language in ["tamil", "ta"]:
                return (
                    f"💧 தமிழ்நாடு குடிநீர் & கழிவுநீரகற்று வாரியம் (1916):\n"
                    f"குடிநீர் புகார் எண்: {complaint_id}\n"
                    f"முன்னுரிமை: {priority} | துறை: {department_name}\n"
                    f"குடிநீர் உதவி பொறியாளர் மற்றும் சீரமைப்பு குழுவிற்கு அனுப்பப்பட்டது.\n"
                    f"நேரடி கண்காணிப்பு: {settings.BASE_URL}/track/{complaint_id}\n"
                    f"குடிநீர் உதவி எண்: 1916 (24x7)"
                )
            elif language == "tanglish":
                return (
                    f"💧 Metro Water & TWAD Board (1916):\n"
                    f"Water Complaint #{complaint_id} registered ({priority}).\n"
                    f"Assigned: {department_name}\n"
                    f"Pipeline repair engineers alerted for inspection.\n"
                    f"Track live: {settings.BASE_URL}/track/{complaint_id}\n"
                    f"Water Helpline: 1916"
                )
            else:
                return (
                    f"💧 Tamil Nadu Water Supply & Drainage Board (1916):\n"
                    f"Grievance Ticket #{complaint_id} registered successfully.\n"
                    f"Assigned Department: {department_name} ({priority})\n"
                    f"Live Status Tracker: {settings.BASE_URL}/track/{complaint_id}\n"
                    f"Toll-Free Helpline: 1916"
                )

        elif category == "Roads":
            if language in ["tamil", "ta"]:
                return (
                    f"🛣️ தமிழ்நாடு நெடுஞ்சாலை & சாலைகள் துறை:\n"
                    f"சாலை புகார் எண்: {complaint_id}\n"
                    f"முன்னுரிமை: {priority} | துறை: {department_name}\n"
                    f"சாலை பராமரிப்பு பணிக்குழுவிற்கு அனுப்பப்பட்டது.\n"
                    f"நேரடி கண்காணிப்பு: {settings.BASE_URL}/track/{complaint_id}\n"
                    f"உதவி எண்: 1800-425-4357"
                )
            else:
                return (
                    f"🛣️ Highways & Corporation Roads Wing:\n"
                    f"Road Grievance Ticket #{complaint_id} registered ({priority}).\n"
                    f"Assigned Department: {department_name}\n"
                    f"Live Status Tracker: {settings.BASE_URL}/track/{complaint_id}\n"
                    f"Helpline: 1800-425-4357"
                )

        elif category == "Sanitation":
            if language in ["tamil", "ta"]:
                return (
                    f"🧹 நகராட்சி நிர்வாகம் & பொது சுகாதாரம் (1913):\n"
                    f"துப்புரவு புகார் எண்: {complaint_id}\n"
                    f"முன்னுரிமை: {priority} | துறை: {department_name}\n"
                    f"துப்புரவு ஆய்வாளர் & தூய்மை குழுவிற்கு அனுப்பப்பட்டுள்ளது.\n"
                    f"நேரடி கண்காணிப்பு: {settings.BASE_URL}/track/{complaint_id}\n"
                    f"மாநகராட்சி உதவி எண்: 1913"
                )
            else:
                return (
                    f"🧹 Municipal Administration & Public Health (1913):\n"
                    f"Sanitation Grievance #{complaint_id} registered ({priority}).\n"
                    f"Assigned Department: {department_name}\n"
                    f"Live Status Tracker: {settings.BASE_URL}/track/{complaint_id}\n"
                    f"GCC / Municipal Helpline: 1913"
                )

        if language in ["tamil", "ta"]:
            return (
                f"🏛️ தமிழ்நாடு அரசு குறைதீர்ப்பு (1077):\n"
                f"உங்கள் புகார் எண்: {complaint_id}\n"
                f"வகை: {category} (முன்னுரிமை: {priority})\n"
                f"ஒதுக்கப்பட்ட துறை: {department_name}\n"
                f"நேரடி கண்காணிப்பு: {settings.BASE_URL}/track/{complaint_id}\n"
                f"பேரிடர் & அரசு உதவி எண்: 1077 / 1800-425-VOXEN"
            )
        elif language == "tanglish":
            return (
                f"🏛️ TN Govt Grievance Redressal:\n"
                f"Unga complaint register aaiduchu! Ticket ID: {complaint_id}\n"
                f"Category: {category} ({priority})\n"
                f"Assigned Dept: {department_name}\n"
                f"Track status live: {settings.BASE_URL}/track/{complaint_id}\n"
                f"Helpline: 1800-425-8693 (24x7)"
            )
        else:
            return (
                f"🏛️ Govt of Tamil Nadu Public Grievance (1077):\n"
                f"Grievance Ticket #{complaint_id} registered successfully.\n"
                f"Category: {category} (Priority: {priority})\n"
                f"Assigned Department: {department_name}\n"
                f"Live Status Tracker: {settings.BASE_URL}/track/{complaint_id}\n"
                f"Toll-Free Helpline: 1800-425-VOXEN / 1077"
            )

    @classmethod
    def send_sms_to_citizen(
        cls,
        phone_number: str,
        message: str,
        complaint_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Dispatches outbound SMS to citizen mobile number.
        If real Twilio credentials exist in .env, sends over telecom network.
        Otherwise provides realistic delivery receipt and stores in live dispatch log.
        """
        formatted_phone = cls.format_phone_number(phone_number)
        timestamp = datetime.datetime.utcnow()
        sms_id = f"SM{int(timestamp.timestamp() * 1000)}"

        delivery_mode = "MOCK_SIMULATED"
        twilio_sid = None

        # Check if real Twilio credentials configured
        if (
            settings.TWILIO_ACCOUNT_SID
            and not settings.TWILIO_ACCOUNT_SID.startswith("AC_dummy")
            and settings.TWILIO_AUTH_TOKEN
            and not settings.TWILIO_AUTH_TOKEN.startswith("dummy")
            and not settings.TWILIO_MOCK_MODE
        ):
            try:
                from twilio.rest import Client
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                msg = client.messages.create(
                    body=message,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=formatted_phone
                )
                twilio_sid = msg.sid
                delivery_mode = "LIVE_TELECOM_TWILIO"
                logger.info(f"Live SMS successfully dispatched via Twilio to {formatted_phone}: SID {msg.sid}")
            except Exception as e:
                logger.error(f"Failed to dispatch live SMS via Twilio: {e}")

        # Check if Exotel credentials configured
        elif (
            settings.EXOTEL_API_KEY
            and not settings.EXOTEL_API_KEY.startswith("voxentra_exotel")
            and not settings.EXOTEL_API_KEY.startswith("your_exotel")
            and settings.EXOTEL_API_TOKEN
            and not settings.EXOTEL_API_TOKEN.startswith("voxentra_exotel")
            and not settings.EXOTEL_API_TOKEN.startswith("your_exotel")
            and settings.EXOTEL_ACCOUNT_SID
        ):
            try:
                import requests
                exotel_url = f"https://api.exotel.com/v1/Accounts/{settings.EXOTEL_ACCOUNT_SID}/Sms/send.json"
                auth = (settings.EXOTEL_API_KEY, settings.EXOTEL_API_TOKEN)
                payload = {
                    "From": settings.EXOTEL_CALLER_ID or "08088919888",
                    "To": formatted_phone,
                    "Body": message
                }
                resp = requests.post(exotel_url, auth=auth, data=payload, timeout=10)
                if resp.status_code in (200, 201):
                    delivery_mode = "LIVE_TELECOM_EXOTEL"
                    logger.info(f"Live SMS successfully dispatched via Exotel to {formatted_phone}")
                else:
                    logger.warning(f"Exotel SMS dispatch response status: {resp.status_code}, {resp.text}")
            except Exception as e:
                logger.error(f"Failed to dispatch live SMS via Exotel: {e}")
                delivery_mode = "FALLBACK_LOCAL"

        record = {
            "sms_id": sms_id,
            "to_phone": formatted_phone,
            "from_sender": "TN-GOVT-VOXEN" if delivery_mode != "LIVE_TELECOM" else settings.TWILIO_PHONE_NUMBER,
            "message": message,
            "complaint_id": complaint_id,
            "status": "Delivered",
            "delivery_mode": delivery_mode,
            "twilio_sid": twilio_sid,
            "timestamp": timestamp.strftime("%d %b %Y, %I:%M:%S %p UTC")
        }

        # Keep last 50 SMS records in buffer
        SENT_SMS_LOG.insert(0, record)
        if len(SENT_SMS_LOG) > 50:
            SENT_SMS_LOG.pop()

        logger.info(f"SMS confirmation logged for {formatted_phone} (Mode: {delivery_mode})")
        return record

    @classmethod
    def send_complaint_confirmation_sms(
        cls,
        phone_number: str,
        complaint_id: str,
        category: str,
        priority: str,
        department_name: str,
        language: str = "tamil"
    ) -> Dict[str, Any]:
        """Convenience method to generate confirmation text and dispatch SMS immediately."""
        text = cls.generate_sms_reply_text(
            complaint_id=complaint_id,
            category=category,
            priority=priority,
            department_name=department_name,
            language=language
        )
        return cls.send_sms_to_citizen(
            phone_number=phone_number,
            message=text,
            complaint_id=complaint_id
        )

    @classmethod
    def get_sent_sms_log(cls, phone_number: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns dispatched SMS history, optionally filtered by phone number."""
        if not phone_number:
            return SENT_SMS_LOG
        formatted = cls.format_phone_number(phone_number)
        return [sms for sms in SENT_SMS_LOG if sms["to_phone"] == formatted or phone_number in sms["to_phone"]]

    @classmethod
    def process_incoming_sms(
        cls,
        db: Session,
        sender_phone: str,
        message_body: str,
        district_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes inbound SMS message, registers complaint, and generates TwiML / response body.
        """
        create_payload = ComplaintCreateText(
            citizen_phone=sender_phone,
            message=message_body.strip(),
            district=district_hint,
            channel="sms"
        )

        complaint = complaint_service.create_text_complaint(
            db=db,
            data=create_payload
        )

        reply_message = cls.generate_sms_reply_text(
            complaint_id=complaint.id,
            category=complaint.category,
            priority=complaint.priority,
            department_name=complaint.department_code or "TN Govt Department",
            language=complaint.language
        )

        # Log outbound delivery
        cls.send_sms_to_citizen(
            phone_number=sender_phone,
            message=reply_message,
            complaint_id=complaint.id
        )

        logger.info(f"SMS Complaint {complaint.id} registered from {sender_phone}. Reply sent.")

        return {
            "status": "success",
            "complaint_id": complaint.id,
            "category": complaint.category,
            "priority": complaint.priority,
            "language": complaint.language,
            "department": complaint.department_code,
            "reply_message": reply_message
        }

    @staticmethod
    def generate_twiml_sms_response(reply_text: str) -> str:
        """
        Wraps message in Twilio TwiML MessagingResponse XML.
        """
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{reply_text}</Message>
</Response>"""


sms_service = SMSService()
