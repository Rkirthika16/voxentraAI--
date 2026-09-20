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
from app.config import settings, TAMIL_NADU_DISTRICTS, CATEGORY_DISPLAY, PRIORITY_LEVELS
from app.database import SessionLocal
from app.schemas.complaint import ComplaintCreateText
from app.services.complaint_service import complaint_service
from app.ai.pipeline import ai_pipeline
from app.ai.transcriber import speech_transcriber
from app.ai.tts import tts_engine, render_autoplay_audio
from app.utils.audio_utils import save_upload_audio_file
from frontend.components.live_map import render_single_ticket_live_map


def _submit_via_fastapi_or_db_text(payload: ComplaintCreateText):
    """Submits text complaint via FastAPI backend endpoint with DB fallback."""
    api_url = f"{settings.BASE_URL}/api/v1/complaints/text"
    try:
        resp = requests.post(api_url, json=payload.model_dump(), timeout=5)
        if resp.status_code in (200, 201):
            data = resp.json()
            # Fetch ORM object for rich rendering
            db = SessionLocal()
            try:
                return complaint_service.get_complaint(db, data["id"])
            finally:
                db.close()
    except Exception:
        pass

    # Direct database fallback
    db = SessionLocal()
    try:
        return complaint_service.create_text_complaint(db=db, data=payload)
    finally:
        db.close()


def _submit_via_fastapi_or_db_voice(
    phone: str,
    audio_bytes: bytes,
    audio_filename: str,
    name: str = None,
    district: str = None,
    location: str = None,
    explicit_text: str = None
):
    """Submits voice grievance via FastAPI backend REST endpoint with DB fallback."""
    api_url = f"{settings.BASE_URL}/api/v1/complaints/voice-upload"
    try:
        files = {"audio_file": (audio_filename, io.BytesIO(audio_bytes), "audio/wav")}
        data = {
            "citizen_phone": phone,
            "citizen_name": name or "",
            "district": district or "",
            "location_details": location or "",
            "explicit_message": explicit_text or ""
        }
        resp = requests.post(api_url, data=data, files=files, timeout=10)
        if resp.status_code in (200, 201):
            res_data = resp.json()
            db = SessionLocal()
            try:
                return complaint_service.get_complaint(db, res_data["id"])
            finally:
                db.close()
    except Exception:
        pass

    # Direct database fallback
    saved_path = save_upload_audio_file(audio_bytes, audio_filename)
    db = SessionLocal()
    try:
        return complaint_service.create_voice_complaint(
            db=db,
            phone_number=phone,
            audio_file_path=saved_path,
            citizen_name=name,
            district=district,
            location_details=location,
            channel="voice_call",
            explicit_message=explicit_text
        )
    finally:
        db.close()


def render_citizen_portal(lang: str = "en"):
    """Renders the Bilingual Citizen Grievance Portal with Conversational AI Voice Officer & Hotline."""
    is_ta = (lang == "ta")

    # Translations dictionary
    T = {
        "title": "பொதுமக்கள் குறைதீர்ப்பு சேவை" if is_ta else "Citizen Public Grievance Portal",
        "subtitle": "தமிழ்நாடு மின் ஆளுமை & AI உதவி சேவை" if is_ta else "Government of Tamil Nadu AI-Powered Redressal System",
        "tab_call": "📞 நேரடி AI குரல் அழைப்பு (Live AI Call)" if is_ta else "📞 Live AI Voice Call",
        "tab_text": "📝 உரை மூலம் புகார் (Text)" if is_ta else "📝 Text Grievance",
        "tab_voice": "🎙️ ஆடியோ பதிவேற்றம் (Audio File)" if is_ta else "🎙️ Audio Upload",
        "tab_track": "🔍 புகார் நிலை அறிதல் (Track)" if is_ta else "🔍 Track Status",
        "tab_emergency": "☎️ தொடர்பு எண்கள் & அவசரம் (Connect Us)" if is_ta else "☎️ Connect Us & Helplines",
        "phone_label": "உங்கள் தொலைபேசி எண் (Mobile Number) *" if is_ta else "Citizen Mobile Number *",
        "name_label": "பெயர் (Full Name - Optional)" if is_ta else "Full Name (Optional)",
        "district_label": "மாவட்டம் (District) *" if is_ta else "District in Tamil Nadu *",
        "location_label": "குறிப்பிட்ட தெரு / பகுதி (Street / Landmark)" if is_ta else "Specific Street, Landmark, Ward",
        "message_label": "புகாரின் விவரம் (Tamil, English, Tanglish-ல் எழுதலாம்) *" if is_ta else "Describe your grievance in Tamil, English, or Tanglish *",
        "message_placeholder": "எ.கா: எங்கள் தெருவில் 3 நாட்களாக குடிநீர் வரவில்லை (அல்லது) Current cut aaiduchi 2 days ah..." if is_ta else "e.g., 3 days ah current illa Anna Nagar la / Water pipe leakage in Katpadi...",
        "submit_btn": "🚀 புகாரைப் பதிவு செய்க (Submit Grievance)" if is_ta else "🚀 Submit Grievance",
        "voice_upload_label": "ஆடியோ கோப்பை பதிவேற்றவும் (.wav, .mp3, .ogg, .m4a)" if is_ta else "Upload Audio File (.wav, .mp3, .ogg, .m4a)",
        "success_title": "🎉 உங்கள் புகார் வெற்றிகரமாக பதிவு செய்யப்பட்டது!" if is_ta else "🎉 Grievance Registered Successfully!",
        "track_id_label": "புகார் எண் (Complaint ID) ஐ உள்ளிடவும்" if is_ta else "Enter Complaint Tracking ID (e.g., TN-WTR-202609-1234)",
        "track_btn": "நிலை சரிபார்க்க (Track Grievance)" if is_ta else "Track Grievance"
    }

    # Header Banner
    st.markdown(f"""
    <div class="tn-header-banner">
        <div>
            <h1 class="tn-header-title">🏛️ {T['title']}</h1>
            <div class="tn-header-subtitle">{T['subtitle']}</div>
        </div>
        <div style="text-align: right;">
            <span style="background: rgba(255,215,0,0.2); color: #ffd700; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.85rem; border: 1px solid #ffd700;">
                TAMIL NADU 24x7 AI
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Prominent 24x7 Connect With Us Hotline Card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(30, 58, 138, 0.5) 0%, rgba(15, 23, 42, 0.8) 100%); border: 1px solid rgba(59, 130, 246, 0.4); border-radius: 12px; padding: 14px 20px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
        <div style="display: flex; align-items: center; gap: 14px;">
            <div style="background: #3b82f6; width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; box-shadow: 0 0 15px rgba(59, 130, 246, 0.6);">
                📞
            </div>
            <div>
                <div style="font-size: 0.85rem; color: #93c5fd; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                    {'அரசு 24x7 கட்டணமில்லா உதவி எண் (Toll-Free Helpline)' if is_ta else '24x7 Government Toll-Free Helpline'}
                </div>
                <div style="font-size: 1.35rem; font-weight: 800; color: #ffffff;">
                    <a href="tel:18004258693" style="color: #ffd700; text-decoration: none;">1800-425-VOXEN</a> <span style="font-size: 0.95rem; color: #cbd5e1; font-weight: 500;">(1800-425-8693)</span>
                </div>
            </div>
        </div>
        <div style="display: flex; gap: 16px; align-items: center;">
            <div style="text-align: right; border-left: 1px solid rgba(255,255,255,0.1); padding-left: 16px;">
                <div style="font-size: 0.75rem; color: #94a3b8;">{'மாநில கட்டுப்பாட்டு அறை' if is_ta else 'State Control Desk'}:</div>
                <div style="font-weight: 700; color: #60a5fa;"><a href="tel:04422334455" style="color: #60a5fa; text-decoration: none;">044-2233-4455</a></div>
            </div>
            <div style="background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color: #34d399; padding: 6px 12px; border-radius: 8px; font-weight: 700; font-size: 0.8rem;">
                🟢 AI ONLINE
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_call, tab_text, tab_voice, tab_track, tab_emergency = st.tabs([
        T["tab_call"],
        T["tab_text"],
        T["tab_voice"],
        T["tab_track"],
        T["tab_emergency"]
    ])

    # =========================================================================
    # TAB 1: LIVE AI VOICE CALL CONVERSATION (TALKING TO CALLER)
    # =========================================================================
    with tab_call:
        st.markdown("### " + ("📞 நேரடி AI குரல் அழைப்பு சேவை (Talk to AI Voice Officer)" if is_ta else "📞 Interactive AI Voice Hotline (Speak & Listen)"))
        st.info("💡 " + (
            "இங்கு நீங்கள் தமிழ்நாடு அரசு AI அதிகாரியிடம் நேரடியாக பேசலாம். உங்கள் குரலில் குறையைக் கூறினால், AI அதிகாரி கேட்டுவிட்டு, "
            "உடனடியாக புகார் எண்ணை உங்களிடம் குரல் வழியே கூறி உரிய துறைக்கு அனுப்பிவைப்பார்!"
            if is_ta else
            "Talk directly to the Government of Tamil Nadu AI Voice Officer! Speak your grievance into the microphone, "
            "and the AI will listen, analyze urgency, register your ticket, and talk back to you with spoken audio confirmation!"
        ))

        # Virtual Phone Call Interface Card
        st.markdown(f"""
        <div style="background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%); border: 2px solid #3b82f6; border-radius: 16px; padding: 20px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5); margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 12px; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 12px; height: 12px; border-radius: 50%; background: #22c55e; box-shadow: 0 0 10px #22c55e;"></div>
                    <span style="font-weight: 700; color: #ffffff; font-size: 1.1rem;">
                        {'தமிழ்நாடு AI குரல் அதிகாரி இணைப்பு' if is_ta else 'Tamil Nadu AI Voice Officer (Live)'}
                    </span>
                </div>
                <div style="background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid #22c55e; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.8rem;">
                    🟢 {'அழைப்பு இணைக்கப்பட்டது' if is_ta else 'CALL CONNECTED'} • 1800-425-VOXEN
                </div>
            </div>
        """, unsafe_allow_html=True)

        # AI Welcome Greeting
        welcome_dialogue = tts_engine.get_ivr_welcome_dialogue(lang="ta" if is_ta else "en")
        
        st.markdown(f"""
        <div style="display: flex; gap: 12px; margin-bottom: 14px; align-items: flex-start;">
            <div style="background: #3b82f6; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; flex-shrink: 0;">
                🤖
            </div>
            <div style="background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 0 12px 12px 12px; padding: 12px 16px; color: #e2e8f0; font-size: 0.95rem;">
                <b>{'AI குரல் அதிகாரி (Greeting)' if is_ta else 'AI Voice Officer (Greeting)'}:</b><br>
                "{welcome_dialogue['active_greeting']}"
            </div>
        </div>
        """, unsafe_allow_html=True)

        if welcome_dialogue.get("audio_bytes"):
            with st.expander("🔊 " + ("அதிகாரியின் தொடக்க குரல் வாழ்த்தை கேட்க (Play Greeting Audio)" if is_ta else "Listen to AI Greeting Voice"), expanded=True):
                st.audio(welcome_dialogue["audio_bytes"], format="audio/mp3")

        st.markdown("---")

        # Caller Input Section
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            caller_phone = st.text_input(T["phone_label"], value="9840112233", key="call_phone")
            caller_name = st.text_input(T["name_label"], placeholder="Karthik / முத்து", key="call_name")
        with c_col2:
            caller_dist = st.selectbox(T["district_label"], ["Auto-detect from Speech"] + TAMIL_NADU_DISTRICTS, key="call_district")
            caller_loc = st.text_input(T["location_label"], placeholder="e.g. Gandhi Nagar Main Road, Katpadi", key="call_loc")

        st.markdown("##### 🎙️ " + ("உங்கள் குறையை மைக்கில் பேசுங்கள் (Speak your complaint):" if is_ta else "Speak your complaint to the AI Officer:"))
        call_audio_input = st.audio_input("Record your voice", key="call_voice_stream")

        call_preset_text = st.text_area(
            "Or type spoken words directly (if microphone is unavailable):",
            placeholder="e.g. Thanni varala 3 days ah Anna Nagar la / Pothole on main road...",
            height=70,
            key="call_text_backup"
        )

        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("📞 " + ("பேசுங்கள் & AI அதிகாரியின் பதிலை கேளுங்கள் (Speak & Listen to AI Officer)" if is_ta else "Submit Call & Listen to AI Response"), type="primary", key="btn_call_submit", use_container_width=True):
            if not caller_phone or len(caller_phone.strip()) < 10:
                st.error("❌ Please provide a valid 10-digit mobile number.")
            elif (call_audio_input is None or len(call_audio_input.getvalue()) == 0) and (not call_preset_text or len(call_preset_text.strip()) < 4):
                st.error("❌ Please speak into the microphone or type your grievance.")
            else:
                with st.spinner("🤖 AI Officer is listening, transcribing, and preparing spoken response..."):
                    explicit_txt = call_preset_text.strip() if call_preset_text else None
                    audio_data = call_audio_input.getvalue() if call_audio_input is not None else None
                    saved_path = save_upload_audio_file(audio_data, "live_call.wav") if audio_data else None

                    selected_dist = caller_dist if caller_dist != "Auto-detect from Speech" else None

                    db = SessionLocal()
                    try:
                        complaint = complaint_service.create_voice_complaint(
                            db=db,
                            phone_number=caller_phone.strip(),
                            audio_file_path=saved_path or "live_call.wav",
                            citizen_name=caller_name.strip() if caller_name else None,
                            district=selected_dist,
                            location_details=caller_loc.strip() if caller_loc else None,
                            channel="voice_call",
                            explicit_message=explicit_txt
                        )

                        # Generate AI Spoken Response
                        dept_name_ta = complaint.department.name_ta if complaint.department else "சம்பந்தப்பட்ட துறை"
                        dept_name_en = complaint.department.name_en if complaint.department else "Concerned Department"

                        call_conv = tts_engine.build_caller_conversation(
                            complaint_id=complaint.id,
                            category=complaint.category,
                            priority=complaint.priority,
                            department_name_ta=dept_name_ta,
                            department_name_en=dept_name_en,
                            lang="ta" if is_ta or complaint.language == "tamil" else "en"
                        )

                        st.success("🎉 " + ("அழைப்பு வெற்றிகரமாக முடிந்தது! AI அதிகாரி பதிலளித்துள்ளார்:" if is_ta else "Call Processed! AI Officer has spoken back to you:"))

                        # Spoken Dialogue Response Box
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(15, 23, 42, 0.9) 100%); border: 2px solid #10b981; border-radius: 12px; padding: 18px; margin: 16px 0;">
                            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                                <div style="background: #10b981; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.1rem;">
                                    🔊
                                </div>
                                <span style="font-weight: 800; color: #34d399; font-size: 1.1rem;">
                                    {'AI அதிகாரி உங்களிடம் பேசுகிறார் (Spoken Voice Reply):' if is_ta else 'AI Voice Officer Speaking Aloud to Caller:'}
                                </span>
                            </div>
                            <div style="color: #f1f5f9; font-size: 1.05rem; line-height: 1.6; background: rgba(0,0,0,0.3); padding: 12px 16px; border-radius: 8px; border-left: 4px solid #10b981;">
                                "{call_conv['active_script']}"
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Audio player for the AI Voice response
                        if call_conv.get("audio_bytes"):
                            st.markdown(render_autoplay_audio(call_conv["audio_bytes"], audio_id=f"voice_reply_{complaint.id}"), unsafe_allow_html=True)

                        # Ticket Card, Live SMS notification & GPS Map
                        _render_complaint_ticket_card(complaint, is_ta)

                    finally:
                        db.close()

    # =========================================================================
    # TAB 2: TEXT GRIEVANCE REGISTRATION
    # =========================================================================
    with tab_text:
        st.markdown("### " + ("புதிய புகாரைப் பதிவு செய்க" if is_ta else "Register a New Complaint"))
        st.info("💡 " + ("தமிழ், English அல்லது Tanglish (எ.கா: 'current cut aaiduchi') மொழிகளில் தட்டச்சு செய்யலாம். AI தானாகவே வகைப்படுத்தி துறைக்கு அனுப்பிவிடும்." if is_ta else "You can write in Tamil script, English, or Tanglish (e.g. 'thanni varala 3 days ah'). AI will automatically detect language, classify category, assess urgency, and route to the correct Tamil Nadu department."))

        col1, col2 = st.columns(2)
        with col1:
            citizen_phone = st.text_input(T["phone_label"], placeholder="9840112233", key="txt_phone")
            citizen_name = st.text_input(T["name_label"], placeholder="Karthik / முத்து", key="txt_name")
        with col2:
            district = st.selectbox(T["district_label"], ["Select District"] + TAMIL_NADU_DISTRICTS, key="txt_district")
            location_details = st.text_input(T["location_label"], placeholder="Anna Nagar West, 4th Main Road", key="txt_loc")

        complaint_text = st.text_area(
            T["message_label"],
            placeholder=T["message_placeholder"],
            height=120,
            key="txt_msg"
        )

        # Real-time AI live inspection preview
        if complaint_text and len(complaint_text.strip()) >= 5:
            with st.expander("⚡ Real-Time AI Live Analysis Preview", expanded=True):
                selected_dist = district if district != "Select District" else None
                analysis = ai_pipeline.process_text_complaint(complaint_text, explicit_district=selected_dist)
                
                c_a, c_b, c_c, c_d = st.columns(4)
                c_a.metric("Detected Language", analysis["detected_language"].title())
                c_b.metric("Category", analysis["category"])
                c_c.metric("Priority", analysis["priority"])
                c_d.metric("AI Confidence", f"{int(analysis['confidence_score'] * 100)}%")

                st.markdown(f"**Assigned TN Department:** `{analysis['department_code']}` - {analysis['department_name_en']} ({analysis['department_name_ta']})")
                if analysis.get("urgency_reason"):
                    st.caption(f"⚠️ **Urgency Note:** {analysis['urgency_reason']}")

        if st.button(T["submit_btn"], type="primary", key="btn_submit_text", use_container_width=True):
            if not citizen_phone or len(citizen_phone.strip()) < 10:
                st.error("❌ Please provide a valid 10-digit mobile phone number.")
            elif not complaint_text or len(complaint_text.strip()) < 5:
                st.error("❌ Please provide a clear grievance description (minimum 5 characters).")
            else:
                with st.spinner("🚀 Submitting grievance via Voxentra AI Pipeline..."):
                    selected_dist = district if district != "Select District" else None
                    payload = ComplaintCreateText(
                        citizen_phone=citizen_phone.strip(),
                        citizen_name=citizen_name.strip() if citizen_name else None,
                        message=complaint_text.strip(),
                        district=selected_dist,
                        location_details=location_details.strip() if location_details else None,
                        channel="web_text"
                    )
                    complaint = _submit_via_fastapi_or_db_text(payload)
                    if complaint:
                        st.success(T["success_title"])
                        _render_complaint_ticket_card(complaint, is_ta)
                    else:
                        st.error("Failed to register complaint.")

    # =========================================================================
    # TAB 2: VOICE & MICROPHONE COMPLAINT REGISTRATION
    # =========================================================================
    with tab_voice:
        st.markdown("### " + ("குரல் பதிவு & மைக்ரோஃபோன் மூலம் புகார்" if is_ta else "Voice & Microphone Grievance Intake"))
        st.info("🎙️ " + ("மைக்ரோஃபோன் மூலம் உங்கள் குரலில் பேசி பதிவு செய்யவும் (அல்லது ஆடியோ கோப்பை பதிவேற்றவும்). OpenAI Whisper AI தானாகவே உரையாக மாற்றி துறைக்கு அனுப்பிவிடும்." if is_ta else "Speak your grievance directly into the microphone or upload an audio file in Tamil, English, or Tanglish. Whisper AI will transcribe, analyze urgency, and route it to the right department."))

        v_col1, v_col2 = st.columns(2)
        with v_col1:
            v_phone = st.text_input(T["phone_label"], placeholder="9840112233", key="voice_phone")
            v_name = st.text_input(T["name_label"], placeholder="Karthik / முத்து", key="voice_name")
        with v_col2:
            v_district = st.selectbox(T["district_label"], ["Select District"] + TAMIL_NADU_DISTRICTS, key="voice_district")
            v_location = st.text_input(T["location_label"], placeholder="Near Srirangam Temple, Tiruchirappalli", key="voice_loc")

        st.markdown("---")
        voice_mode = st.radio(
            "🎙️ " + ("குரல் பதிவு செய்யும் முறை (Audio Input Method):" if is_ta else "Choose Voice Input Method:"),
            ["🔴 Live Microphone (நேரடி மைக்ரோஃபோன் பதிவு)", "📁 Upload Audio File (ஆடியோ கோப்பு பதிவேற்றம்)"],
            horizontal=True
        )

        active_audio_bytes = None
        active_audio_filename = "recorded_voice.wav"

        if "Live Microphone" in voice_mode:
            st.markdown("##### 🎙️ Speak into your Microphone / மைக்கில் பேசவும்:")
            st.caption("Click the red record button, speak your grievance in Tamil, English, or Tanglish, and click stop.")
            mic_audio = st.audio_input("Record Grievance Audio", key="citizen_mic_stream")
            if mic_audio is not None:
                active_audio_bytes = mic_audio.read()
                active_audio_filename = "mic_recording.wav"
                st.audio(active_audio_bytes, format="audio/wav")
        else:
            uploaded_audio = st.file_uploader(
                T["voice_upload_label"],
                type=["wav", "mp3", "ogg", "m4a", "webm"],
                key="voice_file_upload"
            )
            if uploaded_audio is not None:
                active_audio_bytes = uploaded_audio.read()
                active_audio_filename = uploaded_audio.name
                st.audio(active_audio_bytes)

        # Real-time Speech-to-Text Preview if audio exists
        spoken_text = ""
        if active_audio_bytes is not None and len(active_audio_bytes) > 0:
            temp_audio_path = save_upload_audio_file(active_audio_bytes, active_audio_filename)
            with st.spinner("🤖 Whisper AI is transcribing your Tanglish / Tamil speech..."):
                trans_result = speech_transcriber.transcribe(temp_audio_path)
                tanglish_text = trans_result.get("tanglish_text", "").strip()
                tamil_script = trans_result.get("tamil_script", "").strip()
                default_text = trans_result.get("text", "").strip()

            st.markdown("##### 📝 " + ("குரல் உரை வடிவம் & எழுத்து முறை (Voice Transcription):" if is_ta else "Whisper AI Voice Transcription:"))

            t_col1, t_col2 = st.columns([1.5, 1])
            with t_col1:
                script_choice = st.radio(
                    "Display Script / எழுத்து வடிவம்:",
                    ["🔤 Tanglish (Colloquial English script)", "📜 தமிழ் (Tamil Unicode Script)"],
                    horizontal=True,
                    key="voice_script_toggle"
                )
            with t_col2:
                st.caption(f"🎙️ **Detected Language:** `{trans_result.get('language', 'tanglish').title()}` | **Engine:** `OpenAI Whisper`")

            active_transcription = tanglish_text if "Tanglish" in script_choice else tamil_script
            if not active_transcription:
                active_transcription = default_text

            spoken_text = st.text_area(
                "You can verify, edit, or add details to the transcribed text before submitting:",
                value=active_transcription,
                height=90,
                key="voice_spoken_text_input"
            )

            # Dual Preview Cards
            if tanglish_text and tamil_script and tanglish_text != tamil_script:
                with st.expander("🔄 View Both Tanglish & Tamil Script Representations", expanded=False):
                    d_c1, d_c2 = st.columns(2)
                    with d_c1:
                        st.markdown("**🔤 Tanglish Representation:**")
                        st.info(tanglish_text)
                    with d_c2:
                        st.markdown("**📜 Tamil Script (தமிழ்):**")
                        st.success(tamil_script)
            
            if spoken_text and len(spoken_text.strip()) > 3:
                with st.expander("⚡ Live AI Department & Priority Routing", expanded=True):
                    selected_dist = v_district if v_district != "Select District" else None
                    analysis = ai_pipeline.process_text_complaint(spoken_text, explicit_district=selected_dist)
                    
                    c_a, c_b, c_c, c_d = st.columns(4)
                    c_a.metric("Detected Language", analysis["detected_language"].title())
                    c_b.metric("Category", analysis["category"])
                    c_b_sub = CATEGORY_DISPLAY.get(analysis["category"], {}).get("icon", "🏛️")
                    c_c.metric("Priority", analysis["priority"])
                    c_d.metric("AI Confidence", f"{int(analysis['confidence_score'] * 100)}%")
                    st.markdown(f"**Assigned Department:** `{analysis['department_code']}` - {analysis['department_name_en']} ({analysis['department_name_ta']})")

        if st.button("🚀 " + ("குரல் புகாரைப் பதிவு செய்க (Submit Voice Complaint)" if is_ta else "Submit Voice Grievance"), type="primary", key="btn_submit_voice", use_container_width=True):
            if not v_phone or len(v_phone.strip()) < 10:
                st.error("❌ Please provide a valid 10-digit mobile phone number.")
            elif active_audio_bytes is None or len(active_audio_bytes) == 0:
                st.error("❌ Please record via microphone or upload an audio file first.")
            else:
                with st.spinner("🤖 Registering grievance with Tamil Nadu Redressal System..."):
                    selected_dist = v_district if v_district != "Select District" else None
                    complaint = _submit_via_fastapi_or_db_voice(
                        phone=v_phone.strip(),
                        audio_bytes=active_audio_bytes,
                        audio_filename=active_audio_filename,
                        name=v_name.strip() if v_name else None,
                        district=selected_dist,
                        location=v_location.strip() if v_location else None,
                        explicit_text=spoken_text.strip() if spoken_text else None
                    )
                    if complaint:
                        st.success(T["success_title"])
                        _render_complaint_ticket_card(complaint, is_ta)
                    else:
                        st.error("Failed to register voice complaint.")

    # =========================================================================
    # TAB 3: TRACK COMPLAINT STATUS
    # =========================================================================
    with tab_track:
        st.markdown("### " + ("புகார் நிலையை அறிய" if is_ta else "Track Grievance Status"))
        
        c_search1, c_search2 = st.columns([3, 1])
        with c_search1:
            search_id = st.text_input(T["track_id_label"], placeholder="e.g., TN-WTR-202609-4102", key="track_search_id")
        with c_search2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            search_clicked = st.button(T["track_btn"], type="primary", use_container_width=True)

        if search_id or search_clicked:
            if search_id.strip():
                db = SessionLocal()
                try:
                    complaint = complaint_service.get_complaint(db=db, complaint_id=search_id.strip())
                    if not complaint:
                        st.warning(f"⚠️ No complaint found with ID '{search_id.strip()}'. Please check and try again.")
                    else:
                        _render_detailed_tracking_view(complaint, is_ta)
                finally:
                    db.close()

    # =========================================================================
    # TAB 5: CONNECT US & 24x7 HELPLINE DIRECTORY
    # =========================================================================
    with tab_emergency:
        st.markdown("### " + ("☎️ எங்களை தொடர்பு கொள்ளவும் & உதவி எண்கள் (Connect With Us)" if is_ta else "☎️ Connect With Us & 24x7 Government Helplines"))
        st.caption("Official direct hotlines, toll-free redresal numbers, and departmental emergency desks across Tamil Nadu.")

        # Master Toll-Free Cards
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(37, 99, 235, 0.2) 0%, rgba(15, 23, 42, 0.8) 100%); border: 2px solid #3b82f6; border-radius: 12px; padding: 18px; margin-bottom: 16px;">
                <div style="color: #93c5fd; font-size: 0.85rem; font-weight: 700; text-transform: uppercase;">Central Grievance Hotline (24x7)</div>
                <div style="font-size: 1.6rem; font-weight: 800; color: #ffd700; margin: 6px 0;">
                    <a href="tel:18004258693" style="color: #ffd700; text-decoration: none;">📞 1800-425-VOXEN</a>
                </div>
                <div style="color: #cbd5e1; font-size: 0.85rem;">Toll-free across Tamil Nadu • AI Multilingual Automated Dispatch</div>
                <div style="margin-top: 10px;">
                    <span style="background: rgba(34, 197, 94, 0.2); color: #4ade80; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 700; border: 1px solid #22c55e;">Tamil • English • Tanglish</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(15, 23, 42, 0.8) 100%); border: 2px solid #10b981; border-radius: 12px; padding: 18px; margin-bottom: 16px;">
                <div style="color: #6ee7b7; font-size: 0.85rem; font-weight: 700; text-transform: uppercase;">State Control Room & Secretariat</div>
                <div style="font-size: 1.6rem; font-weight: 800; color: #34d399; margin: 6px 0;">
                    <a href="tel:04422334455" style="color: #34d399; text-decoration: none;">☎️ 044-2233-4455</a>
                </div>
                <div style="color: #cbd5e1; font-size: 0.85rem;">Direct Line: Fort St. George, Chennai • Public Redressal Wing</div>
                <div style="margin-top: 10px;">
                    <span style="background: rgba(59, 130, 246, 0.2); color: #93c5fd; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 700; border: 1px solid #3b82f6;">SMS: 56070 • WhatsApp: +91 98401 12233</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### 🚨 Departmental Emergency Helplines")
        e1, e2, e3 = st.columns(3)
        with e1:
            st.markdown("""
            <div class="emergency-pill">
                <div style="font-size: 1.4rem; font-weight: 800;"><a href="tel:100" style="color: #ef4444; text-decoration: none;">📞 100 / 112</a></div>
                <div>Police Control / காவல்துறை</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            st.markdown("""
            <div class="emergency-pill">
                <div style="font-size: 1.4rem; font-weight: 800;"><a href="tel:1912" style="color: #facc15; text-decoration: none;">⚡ 1912</a></div>
                <div>TANGEDCO (TNEB) Electricity</div>
            </div>
            """, unsafe_allow_html=True)
        with e2:
            st.markdown("""
            <div class="emergency-pill">
                <div style="font-size: 1.4rem; font-weight: 800;"><a href="tel:108" style="color: #10b981; text-decoration: none;">🚑 108</a></div>
                <div>Medical Ambulance / மருத்துவ உதவி</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            st.markdown("""
            <div class="emergency-pill">
                <div style="font-size: 1.4rem; font-weight: 800;"><a href="tel:1916" style="color: #38bdf8; text-decoration: none;">💧 1916</a></div>
                <div>TWAD / CMWSSB Metro Water</div>
            </div>
            """, unsafe_allow_html=True)
        with e3:
            st.markdown("""
            <div class="emergency-pill">
                <div style="font-size: 1.4rem; font-weight: 800;"><a href="tel:1077" style="color: #a855f7; text-decoration: none;">🌊 1077</a></div>
                <div>Disaster Control / பேரிடர் மேலாண்மை</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            st.markdown("""
            <div class="emergency-pill">
                <div style="font-size: 1.4rem; font-weight: 800;"><a href="tel:1913" style="color: #ec4899; text-decoration: none;">🧹 1913</a></div>
                <div>GCC / Municipal Sanitation</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 📧 Written Grievances & Digital Ingestion")
        st.markdown("""
        - 📧 **Official Nodal Email:** `grievance.redressal@tn.gov.in`
        - 💬 **WhatsApp Grievance Assistant:** `+91 98401 12233`
        - 📱 **SMS Ingestion Service:** Send `GRIEVANCE <text>` to **`56070`**
        - 🏢 **Postal Redressal Address:** Public Grievance Redressal Cell, Ground Floor, Secretariat, Fort St. George, Chennai - 600009.
        """)

def _render_complaint_ticket_card(complaint, is_ta: bool):
    """Renders formatted ticket summary card and live citizen SMS delivery notification."""
    from app.services.sms_service import sms_service
    
    badge_cls = "badge-emergency" if complaint.priority == "Emergency" else ("badge-high" if complaint.priority == "High" else "badge-medium")
    dept_name = complaint.department.name_en if complaint.department else (complaint.department_code or "TN Govt Department")
    
    # Generate exact SMS text
    sms_text = sms_service.generate_sms_reply_text(
        complaint_id=complaint.id,
        category=complaint.category,
        priority=complaint.priority,
        department_name=dept_name,
        language="tamil" if is_ta or complaint.language == "tamil" else "english"
    )

    st.markdown(f"""
    <div style="background: rgba(16, 185, 129, 0.1); border: 2px solid #10b981; border-radius: 12px; padding: 20px; margin-top: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 1.3rem; font-weight: 800; color: #ffd700;">Ticket ID: {complaint.id}</span>
            <span class="{badge_cls}">{complaint.priority} Priority</span>
        </div>
        <hr style="border-color: rgba(255,255,255,0.1); margin: 12px 0;">
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
            <div>
                <small style="color: #94a3b8;">Category / துறை:</small>
                <div style="font-weight: 700; color: #ffffff;">{complaint.category}</div>
            </div>
            <div>
                <small style="color: #94a3b8;">Department / பிரிவு:</small>
                <div style="font-weight: 700; color: #ffffff;">{complaint.department_code}</div>
            </div>
            <div>
                <small style="color: #94a3b8;">Status / நிலை:</small>
                <div style="font-weight: 700; color: #facc15;">{complaint.status}</div>
            </div>
        </div>
        <div style="margin-top: 12px;">
            <small style="color: #94a3b8;">Transcribed / Registered Message:</small>
            <div style="color: #e2e8f0; font-style: italic; background: rgba(0,0,0,0.2); padding: 8px 12px; border-radius: 6px; margin-top: 4px;">
                "{complaint.original_message}"
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Live Citizen Mobile Phone SMS Handset Notification Box
    st.markdown(f"""
    <div style="background: #090d16; border: 2px solid #38bdf8; border-radius: 14px; padding: 18px; margin-top: 16px; box-shadow: 0 8px 20px rgba(0,0,0,0.4);">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.2rem;">📱</span>
                <span style="font-weight: 800; color: #38bdf8; font-size: 1rem;">
                    {'குடிமகன் மொபைலுக்கு அனுப்பப்பட்ட SMS (Live SMS Delivered)' if is_ta else 'SMS Confirmation Dispatched to Citizen Handset'}
                </span>
            </div>
            <div style="background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid #22c55e; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 700;">
                ✅ DELIVERED
            </div>
        </div>
        <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 8px;">
            <b>To Mobile:</b> <span style="color: #ffd700; font-weight: 700;">{complaint.citizen_phone}</span> &nbsp;|&nbsp; <b>Sender ID:</b> <code>TN-GOVT-VOXEN</code>
        </div>
        <div style="background: rgba(30, 41, 59, 0.9); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 8px; padding: 14px; color: #f8fafc; font-family: monospace; font-size: 0.9rem; line-height: 1.6; white-space: pre-line;">
{sms_text}
        </div>
        <div style="margin-top: 8px; color: #64748b; font-size: 0.75rem; text-align: right;">
            ⚡ Dispatched via Tamil Nadu E-Governance SMS Gateway & Telephony Service
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(f"📲 Resend SMS Confirmation to {complaint.citizen_phone}", key=f"resend_sms_{complaint.id}"):
        sms_service.send_complaint_confirmation_sms(
            phone_number=complaint.citizen_phone,
            complaint_id=complaint.id,
            category=complaint.category,
            priority=complaint.priority,
            department_name=dept_name,
            language="tamil" if is_ta or complaint.language == "tamil" else "english"
        )
        st.toast(f"✅ SMS successfully re-dispatched to {complaint.citizen_phone}!", icon="📱")

def _render_detailed_tracking_view(complaint, is_ta: bool):
    """Renders complete status progression and audit timeline."""
    st.markdown(f"#### 📄 Complaint Record: `{complaint.id}`")

    # Status Progress Bar
    status_steps = ["Pending", "Under Review", "Assigned", "In Progress", "Resolved"]
    current_idx = status_steps.index(complaint.status) if complaint.status in status_steps else 0
    progress_val = int((current_idx / (len(status_steps) - 1)) * 100) if complaint.status != "Rejected" else 100

    st.progress(progress_val)
    st.caption(f"Current Lifecycle Stage: **{complaint.status}** ({progress_val}% completed)")

    # Metadata Grid
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Category", complaint.category)
    m2.metric("Priority", complaint.priority)
    m3.metric("Language", complaint.language.title())
    m4.metric("District", complaint.location_district or "Tamil Nadu")

    st.markdown(f"**Assigned Department:** `{complaint.department_code}` | **Channel:** `{complaint.channel}` | **Registered At:** `{complaint.created_at.strftime('%Y-%m-%d %H:%M UTC')}`")

    st.markdown("##### 📜 Grievance Description")
    st.info(complaint.original_message)

    if complaint.audio_file_path and os.path.exists(complaint.audio_file_path):
        st.markdown("##### 🔊 Original Voice Recording")
        st.audio(complaint.audio_file_path)

    # Live GIS Map & Field Unit Tracker
    st.markdown("##### 🗺️ " + ("நேரடி வரைபடம் & களப்பணியாளர் கண்காணிப்பு (Live GPS Tracker):" if is_ta else "Live GIS Incident & Zonal Field Unit Tracker:"))
    render_single_ticket_live_map(complaint)

    # Status History Audit Trail
    st.markdown("##### ⏱️ Official Action & Audit Trail")
    if complaint.status_history:
        st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
        for entry in complaint.status_history:
            st.markdown(f"""
            <div class="timeline-item">
                <div class="timeline-time">{entry.timestamp.strftime('%d %b %Y, %I:%M %p')} - Changed by: <b>{entry.changed_by}</b></div>
                <div class="timeline-title">Status: <span class="status-badge status-inprogress">{entry.new_status}</span></div>
                <div class="timeline-desc">{entry.remarks or 'No remarks provided.'}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.caption("No history entries recorded yet.")
