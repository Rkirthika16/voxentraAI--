import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class StatusHistoryRead(BaseModel):
    id: int
    complaint_id: str
    previous_status: Optional[str] = None
    new_status: str
    changed_by: str
    remarks: Optional[str] = None
    timestamp: datetime.datetime

    class Config:
        from_attributes = True

class ComplaintCreateText(BaseModel):
    citizen_phone: str = Field(..., description="10-digit Indian phone number or international standard", min_length=10, max_length=15)
    citizen_name: Optional[str] = Field(None, description="Name of the citizen registering grievance")
    message: str = Field(..., description="Grievance description in Tamil, English, or Tanglish", min_length=3)
    district: Optional[str] = Field(None, description="Explicit district or area in Tamil Nadu")
    location_details: Optional[str] = Field(None, description="Specific street, landmark, or ward")
    latitude: Optional[float] = Field(None, description="GPS Latitude coordinate")
    longitude: Optional[float] = Field(None, description="GPS Longitude coordinate")
    channel: Optional[str] = Field("web_text", description="Channel: web_text, sms, voice_call, voice_upload")

class ComplaintUpdateStatus(BaseModel):
    new_status: str = Field(..., description="New status: Pending, Under Review, Assigned, In Progress, Resolved, Rejected")
    changed_by: str = Field("Officer", description="Name or role of the officer updating status")
    remarks: Optional[str] = Field(None, description="Resolution or action remarks")
    department_code: Optional[str] = Field(None, description="Optional reassignment to new department code")
    assigned_officer: Optional[str] = Field(None, description="Name of the assigned field officer")

class AIAnalysisResult(BaseModel):
    original_text: str
    transcribed_text: Optional[str] = None
    detected_language: str
    category: str
    priority: str
    department_code: str
    department_name_en: str
    department_name_ta: str
    extracted_district: Optional[str] = None
    confidence_score: float
    keywords_matched: List[str] = []
    urgency_reason: Optional[str] = None

class ComplaintRead(BaseModel):
    id: str
    citizen_phone: str
    channel: str
    original_message: str
    transcribed_text: Optional[str] = None
    english_translation: Optional[str] = None
    language: str
    category: str
    priority: str
    ai_confidence: float
    location_district: Optional[str] = None
    location_details: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    department_id: Optional[int] = None
    department_code: Optional[str] = None
    status: str
    assigned_officer: Optional[str] = None
    resolution_notes: Optional[str] = None
    audio_file_path: Optional[str] = None
    audio_duration_sec: Optional[float] = None
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    resolved_at: Optional[datetime.datetime] = None
    status_history: List[StatusHistoryRead] = []

    class Config:
        from_attributes = True

class ComplaintListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[ComplaintRead]

class DashboardMetricsResponse(BaseModel):
    total_complaints: int
    pending_count: int
    under_review_count: int
    in_progress_count: int
    resolved_count: int
    rejected_count: int
    emergency_count: int
    high_priority_count: int
    category_breakdown: dict
    priority_breakdown: dict
    channel_breakdown: dict
    district_breakdown: dict
