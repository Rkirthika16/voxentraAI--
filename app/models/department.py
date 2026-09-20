import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name_en = Column(String(150), nullable=False)
    name_ta = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)  # 'Water', 'Electricity', 'Roads', 'Sanitation', 'Other'
    contact_email = Column(String(100), nullable=True)
    helpline_number = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    complaints = relationship("Complaint", back_populates="department")

    def __repr__(self):
        return f"<Department(code={self.code}, category={self.category})>"
