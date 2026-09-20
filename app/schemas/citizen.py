import datetime

from typing import Optional
from pydantic import BaseModel, Field

class CitizenBase(BaseModel):
    phone_number: str = Field(..., description="Citizen contact phone number (10-12 digits)")
    full_name: Optional[str] = Field(None, description="Citizen's full name")
    preferred_language: Optional[str] = Field("tamil", description="Preferred language (tamil, english, tanglish)")
    district: Optional[str] = Field(None, description="District name in Tamil Nadu")

class CitizenCreate(CitizenBase):
    pass

class CitizenRead(CitizenBase):
    id: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True
