import os

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.database import SessionLocal, init_db
from app.models.citizen import Citizen
from app.models.department import Department
from app.models.complaint import Complaint
from app.models.history import ComplaintStatusHistory


def setup_database():
    init_db()

def test_database_department_initialization():
    db = SessionLocal()
    try:
        departments = db.query(Department).all()
        assert len(departments) >= 5
        codes = [d.code for d in departments]
        assert "TANGEDCO" in codes
        assert "TWAD_CMWSSB" in codes
        assert "HIGHWAYS_CORP" in codes
        assert "SANITATION_HEALTH" in codes
        assert "REVENUE_DISASTER" in codes
    finally:
        db.close()

import uuid

def test_citizen_complaint_relation():
    db = SessionLocal()
    test_id = uuid.uuid4().hex[:6]
    test_phone = f"+9199{uuid.uuid4().int % 100000000:08d}"
    try:
        citizen = Citizen(
            phone_number=test_phone,
            full_name=f"Sundararajan {test_id}",
            district="Chennai"
        )
        db.add(citizen)
        db.flush()

        complaint_id = f"TN-OTH-202609-{test_id}"
        complaint = Complaint(
            id=complaint_id,
            citizen_id=citizen.id,
            citizen_phone=citizen.phone_number,
            channel="web_text",
            original_message="Encroachment on public road near park",
            language="english",
            category="Other",
            priority="Low",
            status="Pending"
        )
        db.add(complaint)
        db.flush()

        history = ComplaintStatusHistory(
            complaint_id=complaint.id,
            previous_status=None,
            new_status="Pending",
            changed_by="System"
        )
        db.add(history)
        db.commit()

        # Check relationships
        fetched_citizen = db.query(Citizen).filter(Citizen.id == citizen.id).first()
        assert len(fetched_citizen.complaints) >= 1
        assert fetched_citizen.complaints[0].id == complaint_id

        fetched_complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        assert fetched_complaint.citizen.full_name == f"Sundararajan {test_id}"
        assert len(fetched_complaint.status_history) == 1
    finally:
        db.close()


def test_detached_instance_relationship_access():
    """Verify that relations on Complaint instances remain accessible after db.close() without DetachedInstanceError."""
    from app.services.complaint_service import complaint_service
    db = SessionLocal()
    try:
        complaints, total = complaint_service.list_complaints(db=db, page_size=5)
    finally:
        db.close()

    assert len(complaints) > 0
    # Must be accessible when detached without raising DetachedInstanceError
    first_c = complaints[0]
    assert isinstance(first_c.status_history, list)
    if first_c.citizen_id:
        assert first_c.citizen is not None

