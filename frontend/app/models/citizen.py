import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Citizen(Base):
    __tablename__ = "citizens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    preferred_language = Column(String(20), default="tamil")  # 'tamil', 'english', 'tanglish'
    district = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    complaints = relationship("Complaint", back_populates="citizen", cascade="all, delete-orphan", lazy="selectin")

    def __repr__(self):
        return f"<Citizen(phone={self.phone_number}, name={self.full_name}, district={self.district})>"
