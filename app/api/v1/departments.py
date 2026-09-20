from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.department import Department

router = APIRouter(prefix="/departments", tags=["Departments"])

class DepartmentRead(BaseModel):
    id: int
    code: str
    name_en: str
    name_ta: str
    category: str
    contact_email: str | None = None
    helpline_number: str | None = None

    class Config:
        from_attributes = True

@router.get("", response_model=List[DepartmentRead])
def list_departments(db: Session = Depends(get_db)):
    """Fetches all registered Tamil Nadu government departments and helplines."""
    departments = db.query(Department).all()
    return departments

@router.get("/{code}", response_model=DepartmentRead)
def get_department(code: str, db: Session = Depends(get_db)):
    """Fetches specific department details by department code (e.g., TANGEDCO, TWAD_CMWSSB)."""
    dept = db.query(Department).filter(Department.code == code).first()
    if not dept:
        raise HTTPException(status_code=404, detail=f"Department with code '{code}' not found.")
    return dept
