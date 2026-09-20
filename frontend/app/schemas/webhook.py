from typing import Optional
from pydantic import BaseModel, Field

class TwilioVoiceIncoming(BaseModel):
    CallSid: Optional[str] = None
    From: Optional[str] = Field(None, alias="From")
    To: Optional[str] = Field(None, alias="To")
    CallStatus: Optional[str] = None
    Direction: Optional[str] = None
    Digits: Optional[str] = None
    SpeechResult: Optional[str] = None

class TwilioVoiceRecording(BaseModel):
    CallSid: Optional[str] = None
    RecordingSid: Optional[str] = None
    RecordingUrl: Optional[str] = None
    RecordingDuration: Optional[str] = None
    From: Optional[str] = Field(None, alias="From")
    To: Optional[str] = Field(None, alias="To")

class TwilioSMSIncoming(BaseModel):
    MessageSid: Optional[str] = None
    From: Optional[str] = Field(None, alias="From")
    To: Optional[str] = Field(None, alias="To")
    Body: Optional[str] = Field(None, alias="Body")
    NumMedia: Optional[str] = "0"
    MediaUrl0: Optional[str] = None

class MockCallSimulationRequest(BaseModel):
    caller_phone: str = Field("+919840112233", description="Phone number of the citizen calling")
    spoken_message: Optional[str] = Field(None, description="Simulated spoken text or transcript")
    district: Optional[str] = Field("Chennai", description="Caller's district in Tamil Nadu")
    audio_file_path: Optional[str] = Field(None, description="Optional path to local audio file")

class MockSMSSimulationRequest(BaseModel):
    sender_phone: str = Field("+919840112233", description="Phone number of the citizen texting")
    message_body: str = Field(..., description="SMS body in Tamil, English, or Tanglish")
    district: Optional[str] = Field(None, description="Optional district mention")
