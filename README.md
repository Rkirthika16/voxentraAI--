# 🏛️ VoxentraAI - Tamil Nadu AI Grievance Redressal System

**VoxentraAI** is a comprehensive, production-ready AI-powered public complaint registration and management system specifically engineered for the State of **Tamil Nadu, India**.

It enables citizens to submit grievances via **Normal Voice Phone Calls, Inbound SMS, Web-based Text, and Uploaded Voice Recordings**, with native understanding of **Tamil (தமிழ்), English, and Tanglish** (Tamil written in English script).

---

## 🌟 Key Features

### 👥 1. Citizen Module
- **Bilingual Interface**: Seamlessly switch between **English** and **தமிழ் (Tamil)**.
- **Multi-Channel Grievance Ingestion**:
  - 📝 **Web Text**: Direct grievance submission with **Real-Time Live AI Classification Preview**.
  - 🎙️ **Voice Upload / Mic**: Audio recording upload (.wav, .mp3, .ogg, .m4a) with automatic speech-to-text.
  - 📞 **Voice Calls (IVR)**: Incoming call greeting in Tamil & English with voice recording and TwiML integration.
  - 💬 **SMS Ingestion**: Inbound SMS messages with instant automated bilingual confirmation replies containing tracking links.
- **Comprehensive Data Capture**: Phone number, citizen name, district, specific landmark/street, and channel.
- **Unique Ticket Generation**: Formal state grievance tracking IDs (e.g. `TN-WTR-202609-4102`, `TN-ELE-202609-8472`).
- **Interactive Grievance Tracker**: Real-time progress bar, assigned department, and audit history log.
- **24x7 Emergency SOS Directory**: Direct helpline contacts for Police (100/112), Ambulance (108), TNEB (1912), Metro Water (1916), Disaster (1077), and GCC (1913).

### 🤖 2. Voxentra AI Module
- **Speech-to-Text**: Whisper AI speech recognition engine for Tamil and English audio.
- **Language Detection**: Automatically differentiates between Tamil Unicode script (`tamil`), Latin script English (`english`), and colloquial Latin transliteration (`tanglish`).
- **Grievance Categorization**:
  - 💧 **Water**: Drinking water supply, pipeline bursts, contamination, borewell/motor faults $\rightarrow$ Routed to **TWAD / CMWSSB**.
  - ⚡ **Electricity**: Power outages, live wire hazards, transformer sparks, streetlights $\rightarrow$ Routed to **TANGEDCO (TNEB)**.
  - 🛣️ **Roads**: Deep potholes, cave-ins, broken speed breakers, highway hazards $\rightarrow$ Routed to **Highways Dept / Corporation Roads Wing**.
  - 🧹 **Sanitation**: Uncollected garbage, overflowing drains, mosquito breeding, foul odor $\rightarrow$ Routed to **Municipal Administration & Public Health**.
  - 🏛️ **Other**: Encroachments, revenue disputes, fallen dry branches, disaster alerts $\rightarrow$ Routed to **Revenue & Disaster Management**.
- **Urgency & Priority Classification**:
  - 🚨 **Emergency**: Live sparking wires, electrocution risks, sewage in drinking water, fatal accident hazards, open manholes.
  - 🟠 **High**: Outages lasting 3+ days, hospital/school vicinity disruptions, main water trunk burst.
  - 🔵 **Medium**: General municipal maintenance, residential streetlight failure, garbage pile.
  - 🟢 **Low**: Routine queries, minor maintenance, non-urgent trimming.
- **District & Locality Extraction**: Extracts all 38 Tamil Nadu districts and localities (e.g., Anna Nagar, Gandhipuram, Simmakkal, Katpadi, Thillai Nagar, Velachery, etc.).

### 🛡️ 3. Officer Command Center
- **Summary Metrics**: Real-time counts of Total, Pending, Under Review, In Progress, Resolved, and Emergency alerts.
- **Interactive Analytics**: Plotly visualizations for Category breakdown, Priority severity triage, Channel distribution, and District grievance volume.
- **Advanced Filtering & Search**: Multi-filter by Ticket ID, phone number, category, priority, status, and district.
- **Ticket Inspection & Resolution**:
  - Audio playback of citizen voice recordings.
  - Original and transcribed text comparison.
  - One-click status transitions (`Pending` $\rightarrow$ `Under Review` $\rightarrow$ `Assigned` $\rightarrow$ `In Progress` $\rightarrow$ `Resolved` $\rightarrow$ `Rejected`).
  - Department and officer reassignment.
  - Detailed resolution notes automatically recorded to the audit trail.

### 📞 4. Telephony & SMS Webhook Simulator
- **Interactive Phone Call Simulator**: Dial the virtual helpline, test IVR greetings in Tamil & English, transcribe simulated calls, and view generated TwiML XML.
- **Interactive SMS Simulator**: Send SMS in Tamil, English, or Tanglish, see real-time NLP classification, and verify automated SMS replies.
- **Ready for Real Carriers**: Works out of the box with Twilio, Exotel, or any standard webhook telephony provider.

---

## 🏗️ Project Architecture & Folder Structure

```
voxen/
├── app/
│   ├── __init__.py
│   ├── config.py                 # Configuration, env vars, TN departments & constants
│   ├── database.py               # SQLAlchemy engine, session maker, init_db
│   ├── models/                   # SQLAlchemy ORM database models
│   │   ├── __init__.py
│   │   ├── citizen.py            # Citizens table
│   │   ├── department.py         # Tamil Nadu Departments table
│   │   ├── complaint.py          # Complaints table
│   │   └── history.py            # ComplaintStatusHistory table
│   ├── schemas/                  # Pydantic validation & response models
│   │   ├── __init__.py
│   │   ├── citizen.py
│   │   ├── complaint.py
│   │   └── webhook.py
│   ├── ai/                       # AI, Speech-to-Text & NLP Engine
│   │   ├── __init__.py
│   │   ├── language_detector.py  # Tamil, English, and Tanglish detector
│   │   ├── nlp_classifier.py     # Multi-lingual category & priority classifier
│   │   ├── transcriber.py        # OpenAI Whisper speech-to-text
│   │   └── pipeline.py           # Unified AI processing pipeline
│   ├── services/                 # Domain business services
│   │   ├── __init__.py
│   │   ├── complaint_service.py  # Grievance lifecycle & database operations
│   │   ├── telephony_service.py  # Voice IVR & TwiML generator
│   │   └── sms_service.py        # SMS processing & confirmation generator
│   ├── api/                      # FastAPI Router & Controllers
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py         # V1 Master Router
│   │       ├── complaints.py     # Citizen & Officer Complaint endpoints
│   │       ├── departments.py    # TN Departments CRUD
│   │       ├── webhooks.py       # Voice & SMS Ingestion Webhooks
│   │       └── analytics.py      # Analytics & Dashboard Metrics
│   └── utils/                    # Helper utilities
│       ├── __init__.py
│       ├── id_generator.py       # Unique Ticket ID Generator (e.g. TN-WTR-202609-1234)
│       ├── seed_data.py          # Realistic Tamil Nadu sample grievance seeder
│       └── audio_utils.py        # Audio saving and test wave synthesis
├── frontend/
│   ├── app.py                    # Streamlit Portal & Dashboard Master Entrypoint
│   └── components/
│       ├── __init__.py
│       ├── styles.py             # Glassmorphism & Tamil Nadu custom CSS
│       ├── citizen_portal.py     # Bilingual Citizen Grievance Portal & Tracker
│       ├── officer_dashboard.py  # Officer Command Center with Plotly Visualizations
│       └── telephony_simulator.py# Interactive Phone Call & SMS Simulator
├── tests/
│   ├── __init__.py
│   ├── test_ai_pipeline.py       # AI NLP & language classification tests
│   ├── test_api_complaints.py    # FastAPI REST endpoints tests
│   ├── test_webhooks.py          # Voice & SMS webhook ingestion tests
│   └── test_database.py          # SQLAlchemy models and relations tests
├── static/
│   └── uploads/                  # Uploaded audio recordings storage
├── .env.example                  # Environment variables template
├── requirements.txt              # Project dependencies
├── run_tests.py                  # Standalone test runner
├── run.py                        # Unified application launcher
└── README.md                     # Documentation
```

---

## 🚀 Quickstart & Setup Guide

### Step 1: Clone and Enter the Project Directory
```bash
cd c:\Users\Akshaya\VoxentraAI\voxen
```

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### Step 3: Run Automated Tests
Verify all 18 backend, AI, database, and webhook tests pass:
```bash
python run_tests.py
```

### Step 4: Launch Application
You can launch both the FastAPI Backend and the Streamlit Frontend simultaneously:
```bash
python run.py --mode all
```

Or launch individually:
- **FastAPI Backend only**:
  ```bash
  python run.py --mode api
  # Accessible at: http://127.0.0.1:8000
  # Interactive API Docs (Swagger UI): http://127.0.0.1:8000/docs
  ```
- **Streamlit Frontend only**:
  ```bash
  python run.py --mode frontend
  # Accessible at: http://localhost:8501
  ```

---

## 📡 REST API Documentation

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | System health check and supported capabilities |
| `POST` | `/api/v1/complaints/text` | Register a new complaint via text (Tamil/English/Tanglish) |
| `POST` | `/api/v1/complaints/voice-upload` | Register a new complaint by uploading audio file |
| `POST` | `/api/v1/complaints/preview-ai` | Get real-time AI classification preview without saving |
| `GET` | `/api/v1/complaints/{id}` | Retrieve complaint details and audit history by Ticket ID |
| `GET` | `/api/v1/complaints` | Officer filtered complaint list with search and pagination |
| `PATCH`| `/api/v1/complaints/{id}/status` | Officer update complaint status, assigned team, and remarks |
| `GET` | `/api/v1/departments` | List all Tamil Nadu government departments and helplines |
| `GET` | `/api/v1/analytics/dashboard-metrics` | Aggregated dashboard metrics and distributions |
| `GET` | `/api/v1/complaints/export/excel` | Download all grievances as a styled Microsoft Excel (`.xlsx`) sheet |
| `GET` | `/api/v1/complaints/export/csv` | Export grievances as a CSV file |
| `GET/POST` | `/api/v1/webhooks/exotel/voice/incoming` | Exotel Incoming Call Webhook (Greeting & IVR) |
| `GET/POST` | `/api/v1/webhooks/exotel/voice/recording` | Exotel Recording Callback (Whisper AI + Ticket creation) |
| `GET/POST` | `/api/v1/webhooks/exotel/sms/incoming` | Exotel Inbound SMS Webhook with auto-reply |
| `POST` | `/api/v1/webhooks/voice/incoming` | Twilio Telephony incoming voice call webhook (returns TwiML) |
| `POST` | `/api/v1/webhooks/voice/recording`| Twilio Telephony call recording callback webhook |
| `POST` | `/api/v1/webhooks/sms/incoming` | Twilio Inbound SMS webhook (returns TwiML auto-reply) |
| `POST` | `/api/v1/webhooks/simulator/call` | Local Telephony Simulator endpoint |
| `POST` | `/api/v1/webhooks/simulator/sms` | Local SMS Simulator endpoint |

### Example 1: Submit Text Grievance (Tanglish)
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/complaints/text" \
  -H "Content-Type: application/json" \
  -d '{
    "citizen_phone": "+919840112233",
    "citizen_name": "Karthik",
    "message": "Anna Nagar la 3 days ah current illa, romba problem ah irukku.",
    "district": "Chennai",
    "location_details": "4th Main Road, Anna Nagar"
  }'
```

**Response:**
```json
{
  "id": "TN-ELE-202609-4821",
  "citizen_phone": "+919840112233",
  "channel": "web_text",
  "original_message": "Anna Nagar la 3 days ah current illa, romba problem ah irukku.",
  "language": "tanglish",
  "category": "Electricity",
  "priority": "High",
  "ai_confidence": 0.88,
  "location_district": "Chennai",
  "location_details": "4th Main Road, Anna Nagar",
  "department_code": "TANGEDCO",
  "status": "Pending",
  "created_at": "2026-09-16T15:35:00Z",
  "status_history": [
    {
      "id": 1,
      "complaint_id": "TN-ELE-202609-4821",
      "new_status": "Pending",
      "changed_by": "AI Registration Engine",
      "remarks": "Auto-classified as Electricity with High priority. Routed to Tamil Nadu Generation and Distribution Corporation (TANGEDCO/TNEB).",
      "timestamp": "2026-09-16T15:35:00Z"
    }
  ]
}
```

---

## 🇮🇳 Exotel India Cloud Telephony Integration

VoxentraAI natively integrates with **Exotel India** Virtual Mobile Numbers and 1800 Toll-Free numbers for citizen grievance registration across Tamil Nadu.

### 1. Configure `.env`
```env
EXOTEL_ACCOUNT_SID=your_exotel_account_sid
EXOTEL_API_KEY=your_exotel_api_key
EXOTEL_API_TOKEN=your_exotel_api_token
EXOTEL_CALLER_ID=08088919888
BASE_URL=https://your-public-url.ngrok-free.app
```

### 2. Exotel App Bazaar Call Flow
In your Exotel Dashboard (`my.exotel.com` $\rightarrow$ **App Bazaar** $\rightarrow$ **Create Flow**):

```
[Citizen Dials 080... / 1800...]
       │
       ▼
[1. Greeting Applet] ──> Speaks Tamil & English Welcome
       │
       ▼
[2. Voicemail / Record Applet] ──> Records Citizen Grievance (max 120s, finish on #)
       │
       ▼
[3. Passthru Applet] ──> POST https://your-domain.ngrok.io/api/v1/webhooks/exotel/voice/recording
       │
       ▼
[Whisper AI + NLP Classification Engine]
       │
       ▼
[Unique Ticket ID Generated: TN-WAT-XXXX / TN-ELE-XXXX]
       │
       ▼
[Spoken Voice Confirmation + Instant Outbound SMS via Exotel REST API]
```

### 3. Exotel Webhook URLs
- **Voice Incoming URL**: `https://your-public-url.ngrok-free.app/api/v1/webhooks/exotel/voice/incoming`
- **Voice Recording Callback**: `https://your-public-url.ngrok-free.app/api/v1/webhooks/exotel/voice/recording`
- **SMS Incoming URL**: `https://your-public-url.ngrok-free.app/api/v1/webhooks/exotel/sms/incoming`

---

## 📞 Twilio Telephony Integration

For international phone numbers:

1. **Configure `.env`**:
   ```env
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=+914422334455
   TWILIO_MOCK_MODE=False
   BASE_URL=https://your-public-url.ngrok-free.app
   ```
2. **Configure Twilio Console**:
   - **Voice URL**: `POST https://your-public-url.ngrok-free.app/api/v1/webhooks/voice/incoming`
   - **Voice Recording Callback**: `POST https://your-public-url.ngrok-free.app/api/v1/webhooks/voice/recording`
   - **SMS Inbound URL**: `POST https://your-public-url.ngrok-free.app/api/v1/webhooks/sms/incoming`

> **Note on Local Development**: For testing without external telephony accounts, use the built-in **Telephony & SMS Simulator** inside the Streamlit portal to test all IVR voice calls, TwiML responses, audio transcriptions, and SMS flows.

---

## 🧪 Testing

Execute the test suite at any time:
```bash
python run_tests.py
```
This verifies all 27 automated tests:
1. **AI Pipeline (10 tests)**: Tamil, English, and Tanglish language detection, keyword & sentiment categorization, and emergency priority detection.
2. **Database (3 tests)**: SQLite schema, relations, citizen lookup, and audit trail records.
3. **FastAPI Endpoints (5 tests)**: Text complaint submission, ID tracking, status updates, and dashboard metrics.
4. **Twilio Webhooks (3 tests)**: Voice IVR TwiML, SMS inbound responses, and simulator endpoints.
5. **Exotel Telephony & Export (6 tests)**: Exotel voice incoming, recording callbacks, duplicate `call_sid` deduplication, inbound SMS, Excel (`.xlsx`), and CSV exports.

---

## 📜 License
Developed for the Government of Tamil Nadu Public Grievance AI Initiative.
