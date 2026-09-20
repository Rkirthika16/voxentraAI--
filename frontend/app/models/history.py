import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ComplaintStatusHistory(Base):
    __tablename__ = "complaint_status_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    complaint_id = Column(String(50), ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    previous_status = Column(String(30), nullable=True)
    new_status = Column(String(30), nullable=False)
    changed_by = Column(String(100), default="System", nullable=False)
    remarks = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    complaint = relationship("Complaint", back_populates="status_history")

    def __repr__(self):
        return f"<ComplaintStatusHistory(complaint_id={self.complaint_id}, from={self.previous_status}, to={self.new_status})>"
