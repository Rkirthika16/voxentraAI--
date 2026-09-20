import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, SessionLocal
from app.models.complaint import Complaint
from app.models.citizen import Citizen

client = TestClient(app)

def setup_db():
    init_db()

def test_exotel_incoming_call_get():
    """Test GET request from Exotel Passthru applet for incoming voice call"""
    response = client.get(
        "/api/v1/webhooks/exotel/voice/incoming",
        params={
            "CallSid": "exo_call_12345",
            "From": "+919876543210",
            "To": "0441234567"
        }
    )
    assert response.status_code == 200
    assert "xml" in response.headers["content-type"]
    assert "<Response>" in response.text
    assert "<Record" in response.text

def test_exotel_incoming_call_post():
    """Test POST request from Exotel Passthru applet for incoming voice call"""
    response = client.post(
        "/api/v1/webhooks/exotel/voice/incoming",
        data={
            "CallSid": "exo_call_67890",
            "From": "09876543210",
            "To": "0441234567"
        }
    )
    assert response.status_code == 200
    assert "xml" in response.headers["content-type"]
    assert "<Response>" in response.text

from unittest.mock import patch

def test_exotel_recording_callback():
    """Test Exotel recording callback creates a grievance ticket and speaks confirmation"""
    with patch("app.api.v1.webhooks.telephony_service.process_call_recording") as mock_process:
        mock_process.return_value = {
            "status": "success",
            "complaint_id": "TN-WAT-202609-881234",
            "category": "Water",
            "priority": "HIGH",
            "transcription": "Water pipe leak in T Nagar",
            "language": "tamil",
            "department": "Water Supply & Sewage (CMWSSB)"
        }
        response = client.post(
            "/api/v1/webhooks/exotel/voice/recording",
            data={
                "CallSid": "exo_rec_call_9999",
                "From": "+919840112233",
                "RecordingUrl": "https://s3.ap-south-1.amazonaws.com/exotel-recordings/test.wav"
            }
        )
        assert response.status_code == 200
        assert "xml" in response.headers["content-type"]
        assert "<Response>" in response.text
        assert "<Say" in response.text
        assert "T N" in response.text

def test_exotel_incoming_sms():
    """Test incoming SMS webhook parsing for Exotel"""
    response = client.post(
        "/api/v1/webhooks/exotel/sms/incoming",
        data={
            "SmsSid": "exo_sms_12345",
            "From": "+919840114455",
            "Body": "Drinking water supply is dirty and contaminated in Tambaram Chennai",
        }
    )
    assert response.status_code == 200
    assert "xml" in response.headers["content-type"]
    assert "<Response>" in response.text
    assert "TN-" in response.text

def test_complaints_export_csv():
    """Test CSV export endpoint"""
    response = client.get("/api/v1/complaints/export/csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "Ticket ID" in response.text
    assert "Department" in response.text

def test_complaints_export_excel():
    """Test Excel (.xlsx) export endpoint"""
    response = client.get("/api/v1/complaints/export/excel")
    assert response.status_code == 200
    assert "spreadsheetml" in response.headers["content-type"] or "csv" in response.headers["content-type"]
    assert len(response.content) > 10
