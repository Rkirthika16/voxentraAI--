import os

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

def test_voice_incoming_webhook():
    response = client.post(
        "/api/v1/webhooks/voice/incoming",
        data={"From": "+919840112233", "CallSid": "CA1234567890"}
    )
    assert response.status_code == 200
    assert "xml" in response.headers["content-type"]
    assert "<Response>" in response.text
    assert "<Record" in response.text

def test_sms_incoming_webhook():
    response = client.post(
        "/api/v1/webhooks/sms/incoming",
        data={
            "From": "+919840112233",
            "Body": "Thanni varala 3 days ah Anna Nagar la. Help pannunga.",
            "MessageSid": "SM1234567890"
        }
    )
    assert response.status_code == 200
    assert "xml" in response.headers["content-type"]
    assert "<Response>" in response.text
    assert "TN-" in response.text

def test_sms_simulator_endpoint():
    payload = {
        "sender_phone": "+919840119988",
        "message_body": "Electric pole spark adikuthu Madurai Simmakkal la",
        "district": "Madurai"
    }
    response = client.post("/api/v1/webhooks/simulator/sms", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Simulated SMS processed successfully."
    assert data["details"]["category"] == "Electricity"
    assert data["details"]["complaint_id"].startswith("TN-")
