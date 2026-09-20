import os

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db


def setup_db():
    init_db()

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_text_complaint():
    payload = {
        "citizen_phone": "+919840998877",
        "citizen_name": "Ramesh Raman",
        "message": "Street lights in Velachery are not working for 5 days.",
        "district": "Chennai",
        "location_details": "100 Feet Road, Velachery",
        "channel": "web_text"
    }
    response = client.post("/api/v1/complaints/text", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"].startswith("TN-")
    assert data["category"] == "Electricity"
    assert data["location_district"] == "Chennai"
    assert data["status"] == "Pending"

def test_get_complaint_by_id():
    # First create
    payload = {
        "citizen_phone": "+919840112244",
        "message": "குடிநீர் விநியோகம் கடந்த 3 நாட்களாக இல்லை.",
        "district": "Madurai"
    }
    create_res = client.post("/api/v1/complaints/text", json=payload)
    complaint_id = create_res.json()["id"]

    # Retrieve
    get_res = client.get(f"/api/v1/complaints/{complaint_id}")
    assert get_res.status_code == 200
    complaint = get_res.json()
    assert complaint["id"] == complaint_id
    assert complaint["category"] == "Water"
    assert len(complaint["status_history"]) >= 1

def test_update_complaint_status():
    payload = {
        "citizen_phone": "+919840112255",
        "message": "Road cave in near bus stop.",
        "district": "Salem"
    }
    create_res = client.post("/api/v1/complaints/text", json=payload)
    complaint_id = create_res.json()["id"]

    update_payload = {
        "new_status": "In Progress",
        "changed_by": "Assistant Engineer",
        "remarks": "Repair team dispatched to the location.",
        "assigned_officer": "AE S. Balaji"
    }
    patch_res = client.patch(f"/api/v1/complaints/{complaint_id}/status", json=update_payload)
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated["status"] == "In Progress"
    assert updated["assigned_officer"] == "AE S. Balaji"
    assert len(updated["status_history"]) >= 2

def test_dashboard_metrics():
    res = client.get("/api/v1/analytics/dashboard-metrics")
    assert res.status_code == 200
    data = res.json()
    assert "total_complaints" in data
    assert "category_breakdown" in data
    assert data["total_complaints"] >= 1
