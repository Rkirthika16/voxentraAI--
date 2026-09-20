import datetime

from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import desc, func

from app.models.citizen import Citizen
from app.models.department import Department
from app.models.complaint import Complaint
from app.models.history import ComplaintStatusHistory
from app.schemas.complaint import ComplaintCreateText, ComplaintUpdateStatus
from app.ai.pipeline import ai_pipeline
from app.utils.id_generator import generate_complaint_id
from app.config import get_district_coordinates
import hashlib

class ComplaintService:
    """Core domain service managing the grievance lifecycle, AI routing, and status transitions."""

    @staticmethod
    def get_or_create_citizen(
        db: Session,
        phone_number: str,
        full_name: Optional[str] = None,
        district: Optional[str] = None,
        language: Optional[str] = "tamil"
    ) -> Citizen:
        citizen = db.query(Citizen).filter(Citizen.phone_number == phone_number).first()
        if not citizen:
            citizen = Citizen(
                phone_number=phone_number,
                full_name=full_name,
                district=district,
                preferred_language=language or "tamil"
            )
            db.add(citizen)
            db.flush()
        else:
            if full_name and not citizen.full_name:
                citizen.full_name = full_name
            if district and not citizen.district:
                citizen.district = district
            db.flush()
        return citizen

    @classmethod
    def create_text_complaint(
        cls,
        db: Session,
        data: ComplaintCreateText
    ) -> Complaint:
        # 1. Run AI analysis on text
        ai_res = ai_pipeline.process_text_complaint(
            text=data.message,
            explicit_district=data.district
        )

        final_district = ai_res["extracted_district"] or data.district

        # 2. Get or create citizen
        citizen = cls.get_or_create_citizen(
            db=db,
            phone_number=data.citizen_phone,
            full_name=data.citizen_name,
            district=final_district,
            language=ai_res["detected_language"]
        )

        # 3. Locate department
        dept = db.query(Department).filter(Department.code == ai_res["department_code"]).first()

        # 4. Generate unique ticket ID
        complaint_id = generate_complaint_id(category=ai_res["category"])

        # Compute coordinates
        lat, lon = data.latitude, data.longitude
        if not lat or not lon:
            base_lat, base_lon = get_district_coordinates(final_district)
            h = int(hashlib.md5(complaint_id.encode()).hexdigest(), 16)
            jitter_lat = ((h % 100) - 50) * 0.0006
            jitter_lon = (((h >> 8) % 100) - 50) * 0.0006
            lat, lon = round(base_lat + jitter_lat, 5), round(base_lon + jitter_lon, 5)

        complaint = Complaint(
            id=complaint_id,
            citizen_id=citizen.id,
            citizen_phone=data.citizen_phone,
            channel=data.channel or "web_text",
            original_message=data.message,
            transcribed_text=None,
            language=ai_res["detected_language"],
            category=ai_res["category"],
            priority=ai_res["priority"],
            ai_confidence=ai_res["confidence_score"],
            location_district=final_district,
            location_details=data.location_details,
            latitude=lat,
            longitude=lon,
            department_id=dept.id if dept else None,
            department_code=ai_res["department_code"],
            status="Pending",
            created_at=datetime.datetime.utcnow()
        )
        db.add(complaint)
        db.flush()

        # 5. Record initial history
        history = ComplaintStatusHistory(
            complaint_id=complaint.id,
            previous_status=None,
            new_status="Pending",
            changed_by="AI Registration Engine",
            remarks=f"Auto-classified as {ai_res['category']} with {ai_res['priority']} priority. Routed to {ai_res['department_name_en']}.",
            timestamp=datetime.datetime.utcnow()
        )
        db.add(history)
        db.commit()
        db.refresh(complaint)

        # 6. Automatic SMS Notification to Citizen Mobile Number
        try:
            from app.services.sms_service import sms_service
            sms_service.send_complaint_confirmation_sms(
                phone_number=data.citizen_phone,
                complaint_id=complaint.id,
                category=complaint.category,
                priority=complaint.priority,
                department_name=ai_res.get("department_name_en") or "TN Government",
                language=complaint.language
            )
        except Exception as e:
            pass

        return complaint

    @classmethod
    def create_voice_complaint(
        cls,
        db: Session,
        phone_number: str,
        audio_file_path: str,
        citizen_name: Optional[str] = None,
        district: Optional[str] = None,
        location_details: Optional[str] = None,
        channel: str = "voice_upload",
        explicit_message: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        call_sid: Optional[str] = None,
        recording_reference: Optional[str] = None
    ) -> Complaint:
        # 0. Deduplication check on Call SID (e.g. Exotel / Twilio webhook retry protection)
        if call_sid and call_sid.strip():
            existing = db.query(Complaint).filter(Complaint.call_sid == call_sid.strip()).first()
            if existing:
                return existing

        # 1. Run AI speech transcription and NLP classification
        if explicit_message and len(explicit_message.strip()) > 0:
            ai_res = ai_pipeline.process_text_complaint(
                text=explicit_message.strip(),
                explicit_district=district
            )
            ai_res["transcribed_text"] = explicit_message.strip()
            ai_res["audio_duration_sec"] = 5.0
        else:
            ai_res = ai_pipeline.process_voice_complaint(
                audio_file_path=audio_file_path,
                explicit_district=district
            )

        final_district = ai_res["extracted_district"] or district

        # 2. Get or create citizen
        citizen = cls.get_or_create_citizen(
            db=db,
            phone_number=phone_number,
            full_name=citizen_name,
            district=final_district,
            language=ai_res["detected_language"]
        )

        dept = db.query(Department).filter(Department.code == ai_res["department_code"]).first()
        complaint_id = generate_complaint_id(category=ai_res["category"])

        # Compute coordinates
        lat, lon = latitude, longitude
        if not lat or not lon:
            base_lat, base_lon = get_district_coordinates(final_district)
            h = int(hashlib.md5(complaint_id.encode()).hexdigest(), 16)
            jitter_lat = ((h % 100) - 50) * 0.0006
            jitter_lon = (((h >> 8) % 100) - 50) * 0.0006
            lat, lon = round(base_lat + jitter_lat, 5), round(base_lon + jitter_lon, 5)

        complaint = Complaint(
            id=complaint_id,
            citizen_id=citizen.id,
            citizen_phone=phone_number,
            channel=channel,
            original_message=ai_res.get("transcribed_text") or "[Voice Message]",
            transcribed_text=ai_res.get("transcribed_text"),
            language=ai_res["detected_language"],
            category=ai_res["category"],
            priority=ai_res["priority"],
            ai_confidence=ai_res["confidence_score"],
            location_district=final_district,
            location_details=location_details,
            latitude=lat,
            longitude=lon,
            department_id=dept.id if dept else None,
            department_code=ai_res["department_code"],
            audio_file_path=audio_file_path,
            audio_duration_sec=ai_res.get("audio_duration_sec"),
            call_sid=call_sid.strip() if call_sid else None,
            recording_reference=recording_reference.strip() if recording_reference else None,
            status="Pending",
            created_at=datetime.datetime.utcnow()
        )
        db.add(complaint)
        db.flush()

        history = ComplaintStatusHistory(
            complaint_id=complaint.id,
            previous_status=None,
            new_status="Pending",
            changed_by="AI Speech Ingestion Engine",
            remarks=f"Transcribed via Whisper ({ai_res.get('detected_language')}). Assigned to {ai_res['department_name_en']} with {ai_res['priority']} priority.",
            timestamp=datetime.datetime.utcnow()
        )
        db.add(history)
        db.commit()
        db.refresh(complaint)

        # 3. Automatic SMS Notification to Citizen Mobile Number
        try:
            from app.services.sms_service import sms_service
            sms_service.send_complaint_confirmation_sms(
                phone_number=phone_number,
                complaint_id=complaint.id,
                category=complaint.category,
                priority=complaint.priority,
                department_name=ai_res.get("department_name_en") or "TN Government",
                language=complaint.language
            )
        except Exception as e:
            pass

        return complaint

    @staticmethod
    def get_complaint(db: Session, complaint_id: str) -> Optional[Complaint]:
        return (
            db.query(Complaint)
            .options(
                selectinload(Complaint.status_history),
                selectinload(Complaint.citizen),
                selectinload(Complaint.department)
            )
            .filter(Complaint.id == complaint_id)
            .first()
        )

    @staticmethod
    def list_complaints(
        db: Session,
        search: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        district: Optional[str] = None,
        department_code: Optional[str] = None,
        channel: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[Complaint], int]:
        query = db.query(Complaint)

        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                (Complaint.id.ilike(search_term)) |
                (Complaint.citizen_phone.ilike(search_term)) |
                (Complaint.original_message.ilike(search_term)) |
                (Complaint.location_details.ilike(search_term))
            )

        if category and category != "All":
            query = query.filter(Complaint.category == category)
        if priority and priority != "All":
            query = query.filter(Complaint.priority == priority)
        if status and status != "All":
            query = query.filter(Complaint.status == status)
        if district and district != "All":
            query = query.filter(Complaint.location_district == district)
        if department_code and department_code != "All":
            query = query.filter(Complaint.department_code == department_code)
        if channel and channel != "All":
            query = query.filter(Complaint.channel == channel)

        total_count = query.count()
        items = (
            query.options(
                selectinload(Complaint.status_history),
                selectinload(Complaint.citizen),
                selectinload(Complaint.department)
            )
            .order_by(desc(Complaint.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total_count

    @staticmethod
    def update_complaint_status(
        db: Session,
        complaint_id: str,
        update_data: ComplaintUpdateStatus
    ) -> Optional[Complaint]:
        complaint = (
            db.query(Complaint)
            .options(
                selectinload(Complaint.status_history),
                selectinload(Complaint.citizen),
                selectinload(Complaint.department)
            )
            .filter(Complaint.id == complaint_id)
            .first()
        )
        if not complaint:
            return None

        previous_status = complaint.status
        complaint.status = update_data.new_status
        complaint.updated_at = datetime.datetime.utcnow()

        if update_data.remarks:
            complaint.resolution_notes = update_data.remarks
        if update_data.assigned_officer:
            complaint.assigned_officer = update_data.assigned_officer
        if update_data.department_code:
            dept = db.query(Department).filter(Department.code == update_data.department_code).first()
            if dept:
                complaint.department_id = dept.id
                complaint.department_code = dept.code

        if update_data.new_status == "Resolved":
            complaint.resolved_at = datetime.datetime.utcnow()

        history = ComplaintStatusHistory(
            complaint_id=complaint.id,
            previous_status=previous_status,
            new_status=update_data.new_status,
            changed_by=update_data.changed_by or "Officer",
            remarks=update_data.remarks or f"Status updated from {previous_status} to {update_data.new_status}.",
            timestamp=datetime.datetime.utcnow()
        )
        db.add(history)
        db.commit()
        db.refresh(complaint)
        return complaint

    @staticmethod
    def get_dashboard_metrics(db: Session) -> Dict[str, Any]:
        total = db.query(Complaint).count()
        pending = db.query(Complaint).filter(Complaint.status == "Pending").count()
        under_review = db.query(Complaint).filter(Complaint.status == "Under Review").count()
        in_progress = db.query(Complaint).filter(Complaint.status == "In Progress").count()
        resolved = db.query(Complaint).filter(Complaint.status == "Resolved").count()
        rejected = db.query(Complaint).filter(Complaint.status == "Rejected").count()
        
        emergency = db.query(Complaint).filter(Complaint.priority == "Emergency").count()
        high_prio = db.query(Complaint).filter(Complaint.priority == "High").count()

        # Category breakdown
        cat_rows = db.query(Complaint.category, func.count(Complaint.id)).group_by(Complaint.category).all()
        category_breakdown = {cat: count for cat, count in cat_rows}

        # Priority breakdown
        prio_rows = db.query(Complaint.priority, func.count(Complaint.id)).group_by(Complaint.priority).all()
        priority_breakdown = {prio: count for prio, count in prio_rows}

        # Channel breakdown
        channel_rows = db.query(Complaint.channel, func.count(Complaint.id)).group_by(Complaint.channel).all()
        channel_breakdown = {chan: count for chan, count in channel_rows}

        # District breakdown
        district_rows = db.query(Complaint.location_district, func.count(Complaint.id)).filter(Complaint.location_district.isnot(None)).group_by(Complaint.location_district).all()
        district_breakdown = {dist: count for dist, count in district_rows}

        return {
            "total_complaints": total,
            "pending_count": pending,
            "under_review_count": under_review,
            "in_progress_count": in_progress,
            "resolved_count": resolved,
            "rejected_count": rejected,
            "emergency_count": emergency,
            "high_priority_count": high_prio,
            "category_breakdown": category_breakdown,
            "priority_breakdown": priority_breakdown,
            "channel_breakdown": channel_breakdown,
            "district_breakdown": district_breakdown
        }

complaint_service = ComplaintService()
