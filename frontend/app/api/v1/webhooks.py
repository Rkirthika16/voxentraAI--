import logging
from typing import Optional
from fastapi import APIRouter, Depends, Request, Form, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.services.telephony_service import telephony_service
from app.services.sms_service import sms_service
from app.schemas.webhook import MockCallSimulationRequest, MockSMSSimulationRequest

logger = logging.getLogger("voxentra.api.webhooks")
router = APIRouter(prefix="/webhooks", tags=["Telephony & SMS Webhooks"])

@router.post("/voice/incoming")
async def voice_incoming_webhook(
    request: Request,
    From: Optional[str] = Form(None),
    CallSid: Optional[str] = Form(None)
):
    """
    Twilio/Exotel Webhook for incoming voice calls.
    Returns TwiML with bilingual IVR greeting and records user's voice message.
    """
    action_url = f"{settings.BASE_URL}{settings.API_PREFIX}/webhooks/voice/recording"
    twiml_content = telephony_service.generate_incoming_call_twiml(action_url=action_url)
    
    logger.info(f"Incoming voice call received from {From} (CallSid: {CallSid})")
    return Response(content=twiml_content, media_type="application/xml")

@router.post("/voice/recording")
async def voice_recording_webhook(
    request: Request,
    From: Optional[str] = Form(None),
    CallSid: Optional[str] = Form(None),
    RecordingUrl: Optional[str] = Form(None),
    RecordingDuration: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Twilio/Exotel Webhook called when voice call recording is ready.
    Downloads the audio, transcribes with Whisper, classifies, and creates complaint.
    """
    caller_phone = From or "+919999900000"
    logger.info(f"Processing voice recording for {caller_phone} from {RecordingUrl}")

    result = telephony_service.process_call_recording(
        db=db,
        caller_phone=caller_phone,
        recording_url=RecordingUrl
    )

    twiml_confirm = telephony_service.generate_recording_confirmation_twiml(
        complaint_id=result["complaint_id"],
        category=result["category"],
        department_name=result.get("department") or "Tamil Nadu Government",
        language=result.get("language") or "tamil"
    )
    return Response(content=twiml_confirm, media_type="application/xml")

@router.post("/sms/incoming")
async def sms_incoming_webhook(
    request: Request,
    From: Optional[str] = Form(None),
    Body: Optional[str] = Form(None),
    MessageSid: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Twilio/Exotel Webhook for incoming SMS messages.
    Processes complaint in Tamil, English, or Tanglish, and replies via TwiML.
    """
    sender_phone = From or "+919999900000"
    message_text = Body or ""
    
    logger.info(f"Incoming SMS from {sender_phone}: {message_text[:50]}...")

    result = sms_service.process_incoming_sms(
        db=db,
        sender_phone=sender_phone,
        message_body=message_text
    )

    twiml_reply = sms_service.generate_twiml_sms_response(reply_text=result["reply_message"])
    return Response(content=twiml_reply, media_type="application/xml")

# ==============================================================================
# Exotel Webhook Endpoints (India Telephony)
# ==============================================================================

def _resolve_public_base_url(request: Request) -> str:
    """Dynamically resolves the public HTTPS base URL for ngrok/reverse proxy."""
    proto = request.headers.get("x-forwarded-proto") or request.url.scheme or "https"
    host = request.headers.get("x-forwarded-host") or request.headers.get("host")
    if host and ("ngrok" in host or "exotel" in host):
        return f"{proto}://{host}"
    return settings.BASE_URL.rstrip("/")

@router.api_route("/exotel/voice/incoming", methods=["GET", "POST"])
async def exotel_voice_incoming(request: Request):
    """
    Exotel Webhook for incoming voice calls.
    Returns bilingual IVR greeting and initiates recording.
    """
    form_data = {}
    try:
        form_data = await request.form()
    except Exception:
        pass
    
    caller = (
        form_data.get("From")
        or form_data.get("CallFrom")
        or request.query_params.get("From")
        or request.query_params.get("CallFrom")
        or "+919999900000"
    )
    call_sid = form_data.get("CallSid") or request.query_params.get("CallSid") or "exo_call"
    
    base_url = _resolve_public_base_url(request)
    action_url = f"{base_url}{settings.API_PREFIX}/webhooks/exotel/voice/recording"
    twiml = telephony_service.generate_incoming_call_twiml(action_url=action_url)
    
    logger.info(f"Exotel Incoming Voice Call from {caller} (CallSid: {call_sid}, ActionUrl: {action_url})")
    return Response(content=twiml, media_type="application/xml")

@router.api_route("/exotel/voice/recording", methods=["GET", "POST"])
async def exotel_voice_recording(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Exotel Webhook called when call recording is available.
    Processes speech AI, creates ticket, and speaks department confirmation.
    """
    form_data = {}
    try:
        form_data = await request.form()
    except Exception:
        pass

    caller = (
        form_data.get("From")
        or form_data.get("CallFrom")
        or form_data.get("DialWhomNumber")
        or request.query_params.get("From")
        or request.query_params.get("CallFrom")
        or "+919999900000"
    )
    
    rec_url = (
        form_data.get("RecordingUrl")
        or form_data.get("RecordingURL")
        or form_data.get("RecordUrl")
        or form_data.get("Legs[0][RecordingUrl]")
        or request.query_params.get("RecordingUrl")
        or request.query_params.get("RecordingURL")
        or request.query_params.get("RecordUrl")
    )
    
    call_sid = form_data.get("CallSid") or request.query_params.get("CallSid")
    
    logger.info(f"Exotel Voice Recording Callback received for {caller}: RecURL={rec_url}, CallSid={call_sid}")
    result = telephony_service.process_call_recording(
        db=db,
        caller_phone=caller,
        recording_url=rec_url
    )

    twiml_confirm = telephony_service.generate_recording_confirmation_twiml(
        complaint_id=result["complaint_id"],
        category=result["category"],
        department_name=result.get("department") or "Tamil Nadu Government",
        language=result.get("language") or "tamil"
    )
    return Response(content=twiml_confirm, media_type="application/xml")

@router.api_route("/exotel/sms/incoming", methods=["GET", "POST"])
async def exotel_sms_incoming(
    request: Request,
    From: Optional[str] = Form(None),
    Body: Optional[str] = Form(None),
    SmsSid: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Exotel Inbound SMS Webhook.
    """
    sender = From or request.query_params.get("From") or request.query_params.get("SmsFrom") or "+919999900000"
    msg = Body or request.query_params.get("Body") or request.query_params.get("SmsBody") or ""

    logger.info(f"Exotel Incoming SMS from {sender}: {msg[:50]}...")
    result = sms_service.process_incoming_sms(
        db=db,
        sender_phone=sender,
        message_body=msg
    )

    twiml_reply = sms_service.generate_twiml_sms_response(reply_text=result["reply_message"])
    return Response(content=twiml_reply, media_type="application/xml")

# ==============================================================================
# Local Development & Interactive Simulator Endpoints
# ==============================================================================

@router.post("/simulator/call", status_code=status.HTTP_201_CREATED)
def simulate_phone_call(
    payload: MockCallSimulationRequest,
    db: Session = Depends(get_db)
):
    """
    Interactive Simulator: Emulates a citizen dialing the IVR and speaking their grievance.
    """
    result = telephony_service.process_call_recording(
        db=db,
        caller_phone=payload.caller_phone,
        local_audio_path=payload.audio_file_path,
        transcription_hint=payload.spoken_message
    )
    return {
        "message": "Simulated Voice Call completed successfully.",
        "details": result
    }

@router.post("/simulator/sms", status_code=status.HTTP_201_CREATED)
def simulate_sms_message(
    payload: MockSMSSimulationRequest,
    db: Session = Depends(get_db)
):
    """
    Interactive Simulator: Emulates a citizen sending an SMS grievance in Tamil/English/Tanglish.
    """
    result = sms_service.process_incoming_sms(
        db=db,
        sender_phone=payload.sender_phone,
        message_body=payload.message_body,
        district_hint=payload.district
    )
    return {
        "message": "Simulated SMS processed successfully.",
        "details": result
    }
