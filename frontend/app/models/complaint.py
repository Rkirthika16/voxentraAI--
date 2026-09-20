import datetime

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(String(50), primary_key=True, index=True)  # Formatted ID e.g., 'TN-ELE-202609-1234'
    citizen_id = Column(Integer, ForeignKey("citizens.id"), nullable=True)
    citizen_phone = Column(String(20), index=True, nullable=False)
    channel = Column(String(30), default="web_text", nullable=False)  # 'web_text', 'voice_upload', 'voice_call', 'sms'
    
    # Text contents
    original_message = Column(Text, nullable=False)
    transcribed_text = Column(Text, nullable=True)
    english_translation = Column(Text, nullable=True)
    
    # AI Classification Metadata
    language = Column(String(20), default="tamil", nullable=False)  # 'tamil', 'english', 'tanglish'
    category = Column(String(50), default="Other", index=True, nullable=False)  # 'Water', 'Electricity', 'Roads', 'Sanitation', 'Other'
    priority = Column(String(20), default="Medium", index=True, nullable=False)  # 'Low', 'Medium', 'High', 'Emergency'
    ai_confidence = Column(Float, default=0.85)
    
    # Location
    location_district = Column(String(50), index=True, nullable=True)
    location_details = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Department & Resolution
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    department_code = Column(String(50), nullable=True)
    
    # Status
    status = Column(String(30), default="Pending", index=True, nullable=False)  # 'Pending', 'Under Review', 'Assigned', 'In Progress', 'Resolved', 'Rejected'
    assigned_officer = Column(String(100), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Audio & Telephony Metadata
    audio_file_path = Column(String(255), nullable=True)
    audio_duration_sec = Column(Float, nullable=True)
    call_sid = Column(String(100), index=True, nullable=True)  # Exotel/Twilio unique Call SID
    recording_reference = Column(String(500), nullable=True)  # Remote Carrier Recording URL
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    citizen = relationship("Citizen", back_populates="complaints", lazy="selectin")
    department = relationship("Department", back_populates="complaints", lazy="selectin")
    status_history = relationship(
        "ComplaintStatusHistory",
        back_populates="complaint",
        cascade="all, delete-orphan",
        order_by="ComplaintStatusHistory.timestamp.desc()",
        lazy="selectin"
    )

    def __repr__(self):
        return f"<Complaint(id={self.id}, category={self.category}, priority={self.priority}, status={self.status})>"
