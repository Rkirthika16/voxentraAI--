import datetime
from sqlalchemy.orm import Session
from app.models.citizen import Citizen
from app.models.department import Department
from app.models.complaint import Complaint
from app.models.history import ComplaintStatusHistory
from app.ai.pipeline import ai_pipeline
from app.utils.id_generator import generate_complaint_id

SAMPLE_COMPLAINTS = [
    # 1. Electricity - Tanglish - Emergency (Live wire)
    {
        "phone": "+919840112233",
        "name": "Karthik Subramanian",
        "district": "Chennai",
        "details": "12th Cross Street, Anna Nagar West",
        "message": "Anna Nagar la periya maram vilundhu live electric wire arunthu rottula thonguthu. Spark adikuthu. Uyirukku aabathu, seekiram aala anupunga!",
        "channel": "voice_call"
    },
    # 2. Water - Tamil - High (No water for 3 days)
    {
        "phone": "+919876543210",
        "name": "முத்துலட்சுமி ராமலிங்கம்",
        "district": "Madurai",
        "details": "காமராஜர் சாலை, சிம்மக்கல்",
        "message": "எங்கள் பகுதியில் கடந்த 3 நாட்களாக குடிநீர் குழாயில் தண்ணீர் வரவில்லை. மக்கள் மிகவும் சிரமப்படுகின்றனர். உடனடியாக குடிநீர் விநியோகம் செய்ய வேண்டும்.",
        "channel": "web_text"
    },
    # 3. Roads - English - High (Deep Potholes / Accidents)
    {
        "phone": "+919444123456",
        "name": "Dr. S. Venkatesh",
        "district": "Coimbatore",
        "details": "Near Gandhipuram Bus Stand Junction",
        "message": "Severe road damage with deep craters on the main junction. Multiple two-wheeler accidents have occurred today. Immediate tar patching required.",
        "channel": "sms"
    },
    # 4. Sanitation - Tanglish - Medium (Garbage pile)
    {
        "phone": "+919123456780",
        "name": "Anitha Rajendran",
        "district": "Salem",
        "details": "Fairlands Main Road, Ward 24",
        "message": "Fairlands la kuppai 4 days ah allala. Romba naatham adikuthu, kosu thollai thaanga mudiyala. Cleaning team anupunga.",
        "channel": "voice_upload"
    },
    # 5. Electricity - Tamil - Medium (Street lights off)
    {
        "phone": "+919789012345",
        "name": "செல்வராஜ் பாண்டியன்",
        "district": "Tiruchirappalli",
        "details": "தில்லை நகர் 4-வது கிராஸ்",
        "message": "எங்கள் தெருவில் கடந்த ஒரு வாரமாக தெருவிளக்குகள் எரியவில்லை. இரவில் திருட்டு பயம் அதிகமாக உள்ளது. மின்விளக்குகளை சரிசெய்யவும்.",
        "channel": "web_text"
    },
    # 6. Water - Tanglish - High (Pipeline burst)
    {
        "phone": "+919360198765",
        "name": "Praveen Kumar",
        "district": "Vellore",
        "details": "Katpadi Road near Railway Station",
        "message": "Katpadi main road la drinking water underground pipeline odanju gallons of thanni waste aaguthu. Sump fill panna mudila.",
        "channel": "sms"
    },
    # 7. Sanitation - English - Emergency (Sewage contamination)
    {
        "phone": "+919500123987",
        "name": "Meenakshi Sundaram",
        "district": "Tirunelveli",
        "details": "Vannarpettai High Ground",
        "message": "Severe sewage drain overflow entering drinking water sumps inside residential houses. Extreme health hazard and epidemic risk.",
        "channel": "voice_call"
    },
    # 8. Other - Tamil - Low (Tree trimming)
    {
        "phone": "+919629876543",
        "name": "கண்ணன் துரைசாமி",
        "district": "Thanjavur",
        "details": "தெற்கு வீதி, பெரிய கோவில் அருகில்",
        "message": "சாலையோரம் உள்ள மரத்தின் காய்ந்த கிளைகள் விழும் நிலையில் உள்ளன. விபத்து ஏற்படும் முன் கிளைகளை வெட்டி அகற்றவும்.",
        "channel": "web_text"
    }
]

def seed_sample_data(db: Session) -> int:
    """
    Seeds realistic Tamil Nadu complaint records if database is empty.
    Returns number of created records.
    """
    existing_count = db.query(Complaint).count()
    if existing_count > 0:
        return 0

    count = 0
    now = datetime.datetime.utcnow()

    for idx, item in enumerate(SAMPLE_COMPLAINTS):
        # 1. Ensure Citizen exists
        citizen = db.query(Citizen).filter(Citizen.phone_number == item["phone"]).first()
        if not citizen:
            citizen = Citizen(
                phone_number=item["phone"],
                full_name=item["name"],
                district=item["district"],
                created_at=now - datetime.timedelta(days=idx)
            )
            db.add(citizen)
            db.flush()

        # 2. Run AI pipeline on complaint text
        ai_res = ai_pipeline.process_text_complaint(
            text=item["message"],
            explicit_district=item["district"]
        )

        complaint_id = generate_complaint_id(category=ai_res["category"])

        # Find department
        dept = db.query(Department).filter(Department.code == ai_res["department_code"]).first()

        # Vary statuses for realistic officer dashboard metrics
        statuses = ["Pending", "Under Review", "In Progress", "Resolved", "Pending", "In Progress", "Under Review", "Resolved"]
        assigned_status = statuses[idx % len(statuses)]
        
        created_time = now - datetime.timedelta(days=7 - idx, hours=idx * 2)

        from app.config import get_district_coordinates
        import hashlib
        base_lat, base_lon = get_district_coordinates(item["district"])
        h = int(hashlib.md5(complaint_id.encode()).hexdigest(), 16)
        jitter_lat = ((h % 100) - 50) * 0.0006
        jitter_lon = (((h >> 8) % 100) - 50) * 0.0006
        lat, lon = round(base_lat + jitter_lat, 5), round(base_lon + jitter_lon, 5)

        complaint = Complaint(
            id=complaint_id,
            citizen_id=citizen.id,
            citizen_phone=citizen.phone_number,
            channel=item["channel"],
            original_message=item["message"],
            transcribed_text=ai_res.get("transcribed_text"),
            english_translation=None,
            language=ai_res["detected_language"],
            category=ai_res["category"],
            priority=ai_res["priority"],
            ai_confidence=ai_res["confidence_score"],
            location_district=item["district"],
            location_details=item["details"],
            latitude=lat,
            longitude=lon,
            department_id=dept.id if dept else None,
            department_code=ai_res["department_code"],
            status=assigned_status,
            assigned_officer=f"AE {item['district']} Zone" if assigned_status != "Pending" else None,
            resolution_notes="Grievance investigated by junior engineer. Field work completed." if assigned_status == "Resolved" else None,
            created_at=created_time,
            updated_at=created_time + datetime.timedelta(hours=2),
            resolved_at=created_time + datetime.timedelta(days=1) if assigned_status == "Resolved" else None
        )
        db.add(complaint)
        db.flush()

        # Add initial status history
        history_init = ComplaintStatusHistory(
            complaint_id=complaint.id,
            previous_status=None,
            new_status="Pending",
            changed_by="AI Auto-Ingestion Engine",
            remarks=f"Registered via {item['channel']}. Auto-classified as {ai_res['category']} with {ai_res['priority']} priority.",
            timestamp=created_time
        )
        db.add(history_init)

        if assigned_status != "Pending":
            history_update = ComplaintStatusHistory(
                complaint_id=complaint.id,
                previous_status="Pending",
                new_status=assigned_status,
                changed_by="Zonal Officer",
                remarks=f"Status advanced to {assigned_status}.",
                timestamp=created_time + datetime.timedelta(hours=1)
            )
            db.add(history_update)

        count += 1

    db.commit()
    return count
