import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.complaint import (
    ComplaintCreateText,
    ComplaintUpdateStatus,
    ComplaintRead,
    ComplaintListResponse,
    AIAnalysisResult
)
from app.services.complaint_service import complaint_service
from app.ai.pipeline import ai_pipeline
from app.utils.audio_utils import save_upload_audio_file

router = APIRouter(prefix="/complaints", tags=["Complaints"])

@router.post("/text", response_model=ComplaintRead, status_code=status.HTTP_201_CREATED)
def register_text_complaint(
    payload: ComplaintCreateText,
    db: Session = Depends(get_db)
):
    """
    Registers a new public grievance via Text input (Tamil, English, or Tanglish).
    Automatically executes AI Language Detection, Category/Priority classification, and Department routing.
    """
    try:
        complaint = complaint_service.create_text_complaint(db=db, data=payload)
        return complaint
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register text complaint: {str(e)}")

@router.post("/voice-upload", response_model=ComplaintRead, status_code=status.HTTP_201_CREATED)
async def register_voice_complaint(
    citizen_phone: str = Form(..., min_length=10, max_length=15),
    citizen_name: Optional[str] = Form(None),
    district: Optional[str] = Form(None),
    location_details: Optional[str] = Form(None),
    explicit_message: Optional[str] = Form(None),
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Registers a new public grievance via Audio Voice Upload (.wav, .mp3, .ogg, .m4a, .webm).
    Transcribes the audio using Whisper AI, detects language, and routes to appropriate department.
    """
    try:
        file_bytes = await audio_file.read()
        if len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="Uploaded audio file is empty.")

        saved_path = save_upload_audio_file(file_bytes, audio_file.filename)
        
        complaint = complaint_service.create_voice_complaint(
            db=db,
            phone_number=citizen_phone,
            audio_file_path=saved_path,
            citizen_name=citizen_name,
            district=district,
            location_details=location_details,
            channel="voice_upload",
            explicit_message=explicit_message
        )
        return complaint
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process voice complaint: {str(e)}")

@router.post("/preview-ai", response_model=AIAnalysisResult)
def preview_ai_analysis(payload: ComplaintCreateText):
    """
    Provides real-time interactive preview of AI classification before the citizen submits.
    """
    try:
        analysis = ai_pipeline.process_text_complaint(
            text=payload.message,
            explicit_district=payload.district
        )
        return AIAnalysisResult(
            original_text=analysis["original_text"],
            transcribed_text=analysis.get("transcribed_text"),
            detected_language=analysis["detected_language"],
            category=analysis["category"],
            priority=analysis["priority"],
            department_code=analysis["department_code"],
            department_name_en=analysis["department_name_en"],
            department_name_ta=analysis["department_name_ta"],
            extracted_district=analysis["extracted_district"],
            confidence_score=analysis["confidence_score"],
            keywords_matched=analysis.get("matched_keywords", []),
            urgency_reason=analysis.get("urgency_reason")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Analysis preview error: {str(e)}")

@router.get("/{complaint_id}", response_model=ComplaintRead)
def get_complaint_details(
    complaint_id: str,
    db: Session = Depends(get_db)
):
    """
    Fetches full complaint details along with complete status history audit log.
    """
    complaint = complaint_service.get_complaint(db=db, complaint_id=complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint with ID '{complaint_id}' not found.")
    return complaint

@router.get("", response_model=ComplaintListResponse)
def list_all_complaints(
    search: Optional[str] = Query(None, description="Search query across ID, phone, description, or location"),
    category: Optional[str] = Query(None, description="Filter by Category"),
    priority: Optional[str] = Query(None, description="Filter by Priority"),
    status: Optional[str] = Query(None, description="Filter by Status"),
    district: Optional[str] = Query(None, description="Filter by District"),
    department_code: Optional[str] = Query(None, description="Filter by Department Code"),
    channel: Optional[str] = Query(None, description="Filter by Channel"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Officer API: Lists and filters all public complaints with pagination.
    """
    items, total = complaint_service.list_complaints(
        db=db,
        search=search,
        category=category,
        priority=priority,
        status=status,
        district=district,
        department_code=department_code,
        channel=channel,
        page=page,
        page_size=page_size
    )
    return ComplaintListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )

@router.patch("/{complaint_id}/status", response_model=ComplaintRead)
def update_complaint_status(
    complaint_id: str,
    payload: ComplaintUpdateStatus,
    db: Session = Depends(get_db)
):
    """
    Officer API: Updates complaint status, reassigns department/officer, and records audit trail.
    """
    updated = complaint_service.update_complaint_status(
        db=db,
        complaint_id=complaint_id,
        update_data=payload
    )
    if not updated:
        raise HTTPException(status_code=404, detail=f"Complaint with ID '{complaint_id}' not found.")
    return updated

@router.get("/export/csv")
def export_complaints_csv(db: Session = Depends(get_db)):
    """
    Exports all grievances as a downloadable CSV spreadsheet.
    """
    import io
    import csv
    from fastapi.responses import Response

    items, _ = complaint_service.list_complaints(db=db, page=1, page_size=10000)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Ticket ID", "Citizen Phone", "Category", "Priority", "Status",
        "District", "Location Details", "Department Code", "Language",
        "Channel", "AI Confidence", "Registered At", "Original Message", "Transcribed Text"
    ])
    for c in items:
        writer.writerow([
            c.id, c.citizen_phone, c.category, c.priority, c.status,
            c.location_district or "", c.location_details or "", c.department_code or "", c.language,
            c.channel, c.ai_confidence, c.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            c.original_message, c.transcribed_text or ""
        ])
    
    csv_bytes = output.getvalue().encode("utf-8-sig")
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=voxentra_grievances_export.csv"}
    )

@router.get("/export/excel")
def export_complaints_excel(db: Session = Depends(get_db)):
    """
    Exports all grievances as a downloadable Microsoft Excel (.xlsx) spreadsheet.
    """
    import io
    import pandas as pd
    from fastapi.responses import Response

    items, _ = complaint_service.list_complaints(db=db, page=1, page_size=10000)
    data = []
    for c in items:
        data.append({
            "Ticket ID": c.id,
            "Citizen Phone": c.citizen_phone,
            "Category": c.category,
            "Priority": c.priority,
            "Status": c.status,
            "District": c.location_district or "Tamil Nadu",
            "Location Details": c.location_details or "",
            "Department": c.department_code or "",
            "Language": c.language.title(),
            "Channel": c.channel,
            "AI Confidence": f"{int(c.ai_confidence * 100)}%",
            "Registered At": c.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "Original Grievance": c.original_message,
            "Whisper Transcript": c.transcribed_text or ""
        })
    
    df = pd.DataFrame(data)
    excel_buffer = io.BytesIO()
    try:
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Grievances')
        excel_bytes = excel_buffer.getvalue()
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = "voxentra_grievances.xlsx"
    except Exception:
        # Fallback to CSV format if openpyxl not present
        csv_str = df.to_csv(index=False)
        excel_bytes = csv_str.encode('utf-8-sig')
        media_type = "text/csv"
        filename = "voxentra_grievances.csv"

    return Response(
        content=excel_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
