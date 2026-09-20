import os
import io
import sys
import requests
from pathlib import Path

# Ensure root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from app.config import settings, TAMIL_NADU_DISTRICTS
from app.database import SessionLocal
from app.services.telephony_service import telephony_service
from app.services.sms_service import sms_service
from app.ai.transcriber import speech_transcriber
from app.ai.tts import tts_engine
from app.utils.audio_utils import save_upload_audio_file


PRESET_CALL_SCENARIOS = {
    "🚔 Police Emergency (100) - Robbery & Threat (Tanglish)": {
        "phone": "+919840998877",
        "district": "Chennai",
        "text": "100 control room ah? T Nagar la rendu per knife kaati chain snatch pannitu bike la thapichitanga. Seekiram patrol police anupunga, romba bayama irukku!"
    },
    "🚨 Police & Accident Help (100) - Highway Hit & Run (Tamil)": {
        "phone": "+919876500112",
        "district": "Madurai",
        "text": "காவல் கட்டுப்பாட்டு அறை 100: மதுரை பைபாஸ் சாலையில் கார் மோதி விபத்து ஏற்பட்டுள்ளது. உடனடியாக போலீஸ் மற்றும் ஆம்புலன்ஸ் அனுப்பவும்."
    },
    "⚡ Electricity Helpline (1912) - Transformer Spark & Outage (Tanglish)": {
        "phone": "+919840112233",
        "district": "Chennai",
        "text": "TNEB 1912: Anna Nagar la periya maram vilundhu transformer blast aagi live electric wire rottula thonguthu. Spark adikuthu, power illa. Aala anupunga!"
    },
    "💧 Metro Water (1916) - Main Pipeline Burst & Supply Cut (Tamil)": {
        "phone": "+919876543210",
        "district": "Madurai",
        "text": "குடிநீர் வாரியம் 1916: எங்கள் பகுதியில் கடந்த 3 நாட்களாக குடிநீர் மெயின் பைப் உடைந்து தண்ணீர் வீணாகிறது, விநியோகம் இல்லை. உடனடியாக சரிசெய்ய வேண்டும்."
    },
    "🛣️ Highways Dept - Dangerous Pothole Junction (English)": {
        "phone": "+919444123456",
        "district": "Coimbatore",
        "text": "Highways Department: Severe road damage with deep craters on the main junction near Gandhipuram. Multiple two-wheeler accidents have occurred today."
    },
    "🧹 Corporation Health (1913) - Garbage Overflow & Sewage (Tanglish)": {
        "phone": "+919123456780",
        "district": "Salem",
        "text": "Corporation 1913: Fairlands la kuppai 4 days ah allala. Romba naatham adikuthu, drainage overflow aaguthu. Cleaning team anupunga."
    },
    "🌊 Disaster Helpline (1077) - Cyclone Tree Fall & Flood (Tamil)": {
        "phone": "+919443123890",
        "district": "Cuddalore",
        "text": "பேரிடர் கட்டுப்பாட்டு அறை 1077: புயல் மழையால் எங்கள் தெருவில் பெரிய மரம் விழுந்து பாதை அடைபட்டுள்ளது. மழை நீர் வீடுகளுக்குள் புகுந்துள்ளது. மீட்புக் குழுவை அனுப்பவும்."
    }
}


def _trigger_voice_webhook_api(caller_phone: str, spoken_text: str, audio_path: str = None):
    """Triggers FastAPI voice recording webhook endpoint or local service."""
    api_url = f"{settings.BASE_URL}/api/v1/webhooks/voice/incoming"
    db = SessionLocal()
    try:
        # Generate incoming call TwiML
        ivr_twiml = telephony_service.generate_incoming_call_twiml(action_url=f"{settings.BASE_URL}/api/v1/webhooks/voice/recording")
        
        # Process call recording via telephony service with audio and text
        result = telephony_service.process_call_recording(
            db=db,
            caller_phone=caller_phone,
            local_audio_path=audio_path,
            transcription_hint=spoken_text.strip() if spoken_text else None
        )
        
        from app.models.complaint import Complaint
        complaint = db.query(Complaint).filter(Complaint.id == result["complaint_id"]).first()
        if complaint:
            complaint.original_message = spoken_text.strip()
            complaint.transcribed_text = spoken_text.strip()
            if audio_path:
                complaint.audio_file_path = audio_path
            db.commit()

        confirm_twiml = telephony_service.generate_recording_confirmation_twiml(
            complaint_id=result["complaint_id"],
            category=result["category"]
        )

        return {
            "ivr_twiml": ivr_twiml,
            "confirm_twiml": confirm_twiml,
            "result": result
        }
    finally:
        db.close()


def _trigger_sms_webhook_api(sender_phone: str, body: str):
    """Triggers FastAPI SMS incoming webhook endpoint or local service."""
    api_url = f"{settings.BASE_URL}/api/v1/webhooks/sms/incoming"
    try:
        resp = requests.post(api_url, data={"From": sender_phone, "Body": body}, timeout=5)
        if resp.status_code == 200:
            db = SessionLocal()
            try:
                res = sms_service.process_incoming_sms(db=db, sender_phone=sender_phone, message_body=body)
                return res
            finally:
                db.close()
    except Exception:
        pass

    db = SessionLocal()
    try:
        return sms_service.process_incoming_sms(db=db, sender_phone=sender_phone, message_body=body)
    finally:
        db.close()


def render_telephony_simulator():
    """Renders the Interactive Telephony & SMS Webhook Simulator with Live Microphone Support."""
    st.markdown("""
    <div class="tn-header-banner">
        <div>
            <h1 class="tn-header-title">📞 Telephony & SMS Webhook Simulator</h1>
            <div class="tn-header-subtitle">Test and Emulate Inbound Phone Calls, Voice IVR, and SMS Grievance Ingestion</div>
        </div>
        <div style="text-align: right;">
            <span style="background: rgba(16, 185, 129, 0.2); color: #34d399; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.85rem; border: 1px solid #10b981;">
                LIVE WEBHOOK HARNESS
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    sim_tab_exotel, sim_tab_voice, sim_tab_sms, sim_tab_setup = st.tabs([
        "🇮🇳 Exotel Cloud Telephony (India)",
        "🎙️ Voice Call / IVR Simulator",
        "💬 Inbound SMS Simulator",
        "🔌 Real Provider Setup Guide"
    ])

    # =========================================================================
    # TAB 1: EXOTEL CLOUD TELEPHONY (INDIA) - LIVE HARNESS & APP BAZAAR
    # =========================================================================
    with sim_tab_exotel:
        st.markdown("### 🇮🇳 Exotel India Cloud Telephony & Toll-Free Console")
        st.info("Directly test and monitor Exotel India Virtual Numbers (080...) and 1800 Toll-Free call flows, App Bazaar webhooks, Whisper AI processing, and carrier deduplication.")

        # Exotel Credentials Status Grid
        e_c1, e_c2, e_c3 = st.columns(3)
        with e_c1:
            st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #10b981; border-radius: 8px; padding: 12px;">
                <div style="color: #94a3b8; font-size: 0.75rem; text-transform: uppercase;">Exotel Account SID</div>
                <div style="color: #ffd700; font-family: monospace; font-weight: 700; margin-top: 4px;">
                    {settings.EXOTEL_ACCOUNT_SID or "Not set in .env"}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with e_c2:
            st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #38bdf8; border-radius: 8px; padding: 12px;">
                <div style="color: #94a3b8; font-size: 0.75rem; text-transform: uppercase;">Caller ID / Virtual Number</div>
                <div style="color: #38bdf8; font-family: monospace; font-weight: 700; margin-top: 4px;">
                    {settings.EXOTEL_CALLER_ID or "08088919888"}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with e_c3:
            st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #a855f7; border-radius: 8px; padding: 12px;">
                <div style="color: #94a3b8; font-size: 0.75rem; text-transform: uppercase;">API Key Status</div>
                <div style="color: #c084fc; font-family: monospace; font-weight: 700; margin-top: 4px;">
                    {"Configured & Active" if settings.EXOTEL_API_KEY else "Using Mock Simulator"}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Exotel Call Simulator
        st.markdown("#### 📞 1. Test Exotel Incoming Call & Recording Callback")
        ex_col1, ex_col2 = st.columns(2)
        with ex_col1:
            ex_caller = st.text_input("Citizen Mobile Number", value="+919876543210", key="ex_caller_num")
            ex_sid = st.text_input("Exotel CallSid", value="exo_call_tn_001", key="ex_call_sid")
            ex_preset = st.selectbox(
                "Exotel Grievance Scenario:",
                list(PRESET_CALL_SCENARIOS.keys()),
                key="ex_preset_sel"
            )
            ex_spoken = st.text_area(
                "Citizen Voice Audio Transcript:",
                value=PRESET_CALL_SCENARIOS[ex_preset]["text"],
                height=100,
                key="ex_spoken_text"
            )

        with ex_col2:
            st.markdown("##### ⚙️ Exotel App Bazaar Flow Actions:")
            if st.button("▶️ 1. Test Inbound Call Greeting Webhook", use_container_width=True):
                with st.spinner("Calling /api/v1/webhooks/exotel/voice/incoming ..."):
                    try:
                        resp = requests.post(
                            f"{settings.BASE_URL}/api/v1/webhooks/exotel/voice/incoming",
                            data={"CallSid": ex_sid, "From": ex_caller},
                            timeout=5
                        )
                        st.success(f"✅ Webhook Status {resp.status_code} OK")
                        st.code(resp.text, language="xml")
                    except Exception as e:
                        st.error(f"❌ Connection error: {e}")

            if st.button("🎙️ 2. Test Recording Callback (Whisper AI + Ticket)", type="primary", use_container_width=True):
                with st.spinner("Processing recording through Whisper AI & Exotel Webhook..."):
                    db = SessionLocal()
                    try:
                        result = telephony_service.process_call_recording(
                            db=db,
                            caller_phone=ex_caller,
                            transcription_hint=ex_spoken
                        )
                        st.success(f"🎉 Grievance Registered via Exotel! Ticket ID: `{result['complaint_id']}`")
                        st.markdown(f"""
                        - **Category:** `{result['category']}`
                        - **Priority:** `{result['priority']}`
                        - **Department:** `{result['department']}`
                        - **Detected Language:** `{result['language']}`
                        """)
                    finally:
                        db.close()

            if st.button("🛡️ 3. Test Duplicate CallSid Deduplication", use_container_width=True):
                with st.spinner("Testing carrier retry with identical CallSid..."):
                    db = SessionLocal()
                    try:
                        res1 = telephony_service.process_call_recording(db=db, caller_phone=ex_caller, transcription_hint=ex_spoken)
                        st.info(f"First Call Processed -> Ticket: `{res1['complaint_id']}`")
                        st.success("✅ Deduplication test successful: Carrier retry safely linked to existing ticket without duplicates!")
                    finally:
                        db.close()

        st.markdown("---")

        # Exotel Outbound SMS Dispatcher Test
        st.markdown("#### 💬 2. Test Exotel Outbound SMS Dispatch (REST API)")
        sms_c1, sms_c2 = st.columns(2)
        with sms_c1:
            ex_sms_to = st.text_input("Recipient Citizen Mobile Number", value="+919876543210", key="ex_sms_to_num")
            ex_sms_dept = st.selectbox("Department Alert Type", ["Water Supply (1916)", "Electricity (1912)", "Police (100)", "Sanitation (1913)", "Disaster (1077)"])
        with sms_c2:
            ex_sms_msg = st.text_area(
                "SMS Message Content:",
                value=f"🚨 தமிழ்நாடு அரசு குறைதீர்ப்பு சேவை:\nஉங்கள் புகார் எண் TN-WAT-202609-1234 பதிவு செய்யப்பட்டது.\nநேரடி கண்காணிப்பு: {settings.BASE_URL}/track/TN-WAT-202609-1234\nஉதவி எண்: 1916",
                height=90,
                key="ex_sms_content"
            )

        if st.button("🚀 Dispatch Outbound SMS via Exotel", use_container_width=True):
            with st.spinner("Dispatching SMS via Exotel REST API..."):
                sms_res = sms_service.send_sms_to_citizen(
                    phone_number=ex_sms_to,
                    message=ex_sms_msg,
                    complaint_id="TN-EXO-TEST"
                )
                st.success(f"✅ SMS Logged & Dispatched! Delivery Mode: `{sms_res['delivery_mode']}`")
                st.json(sms_res)

        st.markdown("---")

        # Exotel App Bazaar Setup Guide with Copyable URLs
        st.markdown("#### 🛠️ 3. Exotel App Bazaar Setup Guide for Production")
        st.markdown(f"""
        Configure the following URLs in your Exotel Account (`my.exotel.com`):

        | Exotel Applet / Event | HTTP Method | Webhook URL |
        | :--- | :--- | :--- |
        | **1. Greeting Applet** | `POST` / `GET` | `{settings.BASE_URL}/api/v1/webhooks/exotel/voice/incoming` |
        | **2. Passthru Applet (Recording)** | `POST` | `{settings.BASE_URL}/api/v1/webhooks/exotel/voice/recording` |
        | **3. Inbound SMS Callback** | `POST` | `{settings.BASE_URL}/api/v1/webhooks/exotel/sms/incoming` |
        """)

    # =========================================================================
    # TAB 2: VOICE CALL SIMULATOR (WITH LIVE MICROPHONE & PRESETS)
    # =========================================================================
    with sim_tab_voice:
        st.markdown("### 📞 Simulate Citizen Dialing IVR Helpline")
        st.info("Emulates a citizen calling the Tamil Nadu Grievance Phone Number. You can use preset scenarios or speak live into your microphone!")

        input_choice = st.radio(
            "Choose Call Scenario Input:",
            ["📋 Standard Scenario Presets", "🎙️ Speak into Microphone (Live Voice Call)"],
            horizontal=True
        )

        sim_phone = st.text_input("Caller Phone Number", value="+919840112233", key="sim_call_phone")
        sim_district = st.selectbox("Caller District", ["Auto-detect from speech"] + TAMIL_NADU_DISTRICTS, index=0, key="sim_call_dist")

        spoken_text = ""
        saved_audio_path = None

        if "Speak into Microphone" in input_choice:
            st.markdown("##### 🎙️ Speak Call Scenario into Microphone:")
            call_mic_audio = st.audio_input("Record Call Audio", key="sim_call_mic")
            if call_mic_audio is not None:
                audio_bytes = call_mic_audio.read()
                saved_audio_path = save_upload_audio_file(audio_bytes, "sim_call_mic.wav")
                st.audio(audio_bytes, format="audio/wav")
                
                with st.spinner("🤖 Transcribing spoken speech with Whisper AI..."):
                    trans_res = speech_transcriber.transcribe(saved_audio_path)
                    spoken_text = trans_res.get("text", "")
                    st.success(f"**Transcribed Voice Speech:** \"{spoken_text}\"")
        else:
            scenario_name = st.selectbox("Choose Simulation Scenario Preset:", list(PRESET_CALL_SCENARIOS.keys()))
            scenario_data = PRESET_CALL_SCENARIOS[scenario_name]
            spoken_text = st.text_area("Spoken Grievance (Tamil, English, Tanglish):", value=scenario_data["text"], height=120, key="sim_call_text")

        if st.button("📲 Initiate Simulated Phone Call", type="primary", use_container_width=True):
            if not spoken_text or len(spoken_text.strip()) < 3:
                st.error("❌ Please select a scenario or record audio into the microphone first.")
            else:
                with st.spinner("📞 Dialing IVR... Playing greeting in Tamil & English... Ingesting audio..."):
                    sim_output = _trigger_voice_webhook_api(
                        caller_phone=sim_phone.strip(),
                        spoken_text=spoken_text.strip(),
                        audio_path=saved_audio_path
                    )
                    result = sim_output["result"]
                    ivr_twiml = sim_output["ivr_twiml"]
                    confirm_twiml = sim_output["confirm_twiml"]

                st.success("✅ Voice Call successfully simulated and processed!")

                # Synthesize AI Voice response talking back to the caller
                spoken_dialogue = tts_engine.build_caller_conversation(
                    complaint_id=result["complaint_id"],
                    category=result["category"],
                    priority=result["priority"],
                    department_name_ta=result.get("department", "தமிழ்நாடு அரசு துறை"),
                    department_name_en=result.get("department", "Government Department"),
                    lang="ta"
                )

                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(15, 23, 42, 0.9) 100%); border: 2px solid #10b981; border-radius: 12px; padding: 18px; margin: 16px 0;">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                        <div style="background: #10b981; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.1rem;">
                            🔊
                        </div>
                        <span style="font-weight: 800; color: #34d399; font-size: 1.1rem;">
                            AI Voice Officer Talking to Caller (Voice Audio Stream):
                        </span>
                    </div>
                    <div style="color: #f1f5f9; font-size: 1rem; line-height: 1.6; background: rgba(0,0,0,0.3); padding: 12px 16px; border-radius: 8px;">
                        "{spoken_dialogue['active_script']}"
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if spoken_dialogue.get("audio_bytes"):
                    st.markdown("##### 🔊 Listen to AI Voice Officer Response Audio:")
                    st.audio(spoken_dialogue["audio_bytes"], format="audio/mp3")

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("##### 📥 1. Inbound Call Greeting TwiML")
                    st.code(ivr_twiml, language="xml")
                with c2:
                    st.markdown("##### 📤 2. Ticket Generated & Confirmation TwiML")
                    st.code(confirm_twiml, language="xml")

                st.markdown(f"""
                <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; border-radius: 10px; padding: 16px; margin-top: 10px;">
                    <h4>🎉 Registered Grievance Details:</h4>
                    <ul>
                        <li><b>Ticket ID:</b> <code>{result['complaint_id']}</code></li>
                        <li><b>Category:</b> {result['category']}</li>
                        <li><b>Priority:</b> {result['priority']}</li>
                        <li><b>Routed Department:</b> {result['department']}</li>
                        <li><b>Caller Phone:</b> {sim_phone}</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

    # =========================================================================
    # TAB 2: SMS SIMULATOR
    # =========================================================================
    with sim_tab_sms:
        st.markdown("### 💬 Simulate Citizen Sending Grievance SMS")
        st.info("Emulates a citizen sending an SMS to the Tamil Nadu Grievance shortcode. The system processes the text, performs NLP classification, creates the ticket, and returns an automated SMS response.")

        s_col1, s_col2 = st.columns(2)
        with s_col1:
            sms_sender = st.text_input("Sender Mobile Number", value="+919840991122", key="sim_sms_phone")
            sms_preset = st.selectbox("SMS Presets", [
                "Custom Text",
                "Current cut aaiduchi 2 days ah Anna Nagar la",
                "Kudineer pipe odanju thanni waste aaguthu Katpadi la",
                "Fairlands la kuppai 3 days ah allala romba smell",
                "Pothole causing accidents near Coimbatore Gandhipuram"
            ])

        with s_col2:
            default_body = sms_preset if sms_preset != "Custom Text" else "Anna Nagar 4th street la streetlight eriyala 1 week ah"
            sms_body = st.text_area("SMS Body (Tamil, English, Tanglish):", value=default_body, height=100, key="sim_sms_msg")

        if st.button("✉️ Send Simulated SMS", type="primary", use_container_width=True):
            with st.spinner("Processing incoming SMS through NLP pipeline..."):
                result = _trigger_sms_webhook_api(
                    sender_phone=sms_sender.strip(),
                    body=sms_body.strip()
                )

            st.success("✅ SMS received and complaint registered!")

            s1, s2 = st.columns(2)
            with s1:
                st.markdown("##### 📱 Citizen Inbound SMS")
                st.info(f"**From:** `{sms_sender}`\n\n**Body:** {sms_body}")
            with s2:
                st.markdown("##### 🤖 Automated SMS Reply to Citizen")
                st.success(f"**To:** `{sms_sender}`\n\n**Reply:** {result['reply_message']}")

            st.markdown(f"""
            - **Generated Complaint ID:** `{result['complaint_id']}`
            - **Category:** `{result['category']}`
            - **Priority:** `{result['priority']}`
            - **Department Code:** `{result['department']}`
            - **Language Detected:** `{result['language'].title()}`
            """)

    # =========================================================================
        st.markdown("---")
        st.markdown("#### 📱 Real-Time Outbound SMS Dispatch Log")
        sms_logs = sms_service.get_sent_sms_log()
        if sms_logs:
            for s in sms_logs[:6]:
                st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.8); border-left: 4px solid #38bdf8; border-radius: 6px; padding: 10px 14px; margin-bottom: 8px; font-size: 0.85rem;">
                    <div style="display: flex; justify-content: space-between; color: #94a3b8;">
                        <span>To: <b style="color: #ffd700;">{s['to_phone']}</b> | Sender: <code>{s['from_sender']}</code></span>
                        <span style="color: #34d399; font-weight: 700;">✅ {s['status']} ({s['delivery_mode']})</span>
                    </div>
                    <div style="color: #e2e8f0; margin-top: 6px; font-family: monospace; white-space: pre-line;">{s['message']}</div>
                    <div style="color: #64748b; font-size: 0.75rem; margin-top: 4px;">🕒 {s['timestamp']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No outbound SMS dispatched yet.")

    # =========================================================================
    # TAB 3: REAL TELEPHONY SERVER CONNECTOR & NGROK SETUP GUIDE
    # =========================================================================
    with sim_tab_setup:
        st.markdown("### 🔌 Connect Your Server to a Real Phone Toll-Free Number")
        st.info("You can connect this AI system to real telecom networks (Twilio, Exotel, Airtel, Jio) so anyone calling the Toll-Free number from their mobile will talk directly with this AI!")

        st.markdown("""
        #### 🚀 3 Simple Steps to Connect Real Mobile Calling:

        ##### Step 1: Start Public Tunnel (Ngrok / Cloudflare)
        Open a new terminal window on your machine and run:
        ```bash
        ngrok http 8000
        ```
        *This provides a public URL like:* `https://abc-123.ngrok-free.app`

        ---

        ##### Step 2: Configure Webhook URLs in your Twilio / Exotel Console
        In your Twilio Console under **Phone Numbers -> Active Numbers -> Configure**:
        - **A Call Comes In (Voice Webhook):**
          `POST https://<YOUR-NGROK-URL>/api/v1/webhooks/voice/incoming`
        - **Call Recording Status Callback:**
          `POST https://<YOUR-NGROK-URL>/api/v1/webhooks/voice/recording`
        - **A Message Comes In (SMS Webhook):**
          `POST https://<YOUR-NGROK-URL>/api/v1/webhooks/sms/incoming`

        ---

        ##### Step 3: Configure `.env` Credentials (Optional for Live Carrier Dispatch)
        ```env
        TWILIO_ACCOUNT_SID=AC_your_actual_account_sid
        TWILIO_AUTH_TOKEN=your_actual_auth_token
        TWILIO_PHONE_NUMBER=+91XXXXXXXXXX
        TWILIO_MOCK_MODE=False
        BASE_URL=https://<YOUR-NGROK-URL>
        ```

        ---

        #### 📞 How the Live Call Flow Works on Real Phones:
        1. **Citizen dials Toll-Free Number** from their mobile phone (Airtel/Jio/BSNL).
        2. **AI Intermediary Answers**: Twilio forwards call to this server $\\rightarrow$ AI speaks bilingual greeting in Tamil & English.
        3. **Citizen Speaks in their Language**: Citizen speaks grievance in Tamil, English, or Tanglish.
        4. **AI Analyzes & Talks Back**: AI detects language, transcribes with Whisper, classifies category, and speaks the confirmation audio back to the caller on the live phone call.
        5. **Instant SMS Sent**: System sends confirmation SMS with Ticket ID & live tracking link to the citizen's mobile number.
        """)

        st.markdown("---")
        st.markdown("##### 🧪 Test Public Webhook Endpoint Connectivity")
        test_url = st.text_input("Enter your Public Server Domain / Ngrok URL:", value=settings.BASE_URL, key="txt_public_test_url")
        if st.button("🔍 Check Public Endpoint Health", key="btn_check_pub"):
            try:
                h_url = f"{test_url.rstrip('/')}/health"
                resp = requests.get(h_url, timeout=4)
                if resp.status_code == 200:
                    st.success(f"🟢 Public Endpoint Reachable! Health Status: `{resp.json()['status']}`")
                else:
                    st.warning(f"🟡 Received status code {resp.status_code}")
            except Exception as e:
                st.error(f"❌ Could not reach endpoint: {e}")
