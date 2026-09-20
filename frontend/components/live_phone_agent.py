import os
import sys
import time
from pathlib import Path

# Ensure root directory in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
import requests
from app.config import settings, TAMIL_NADU_DISTRICTS
from app.database import SessionLocal
from app.services.telephony_service import telephony_service
from app.services.sms_service import sms_service
from app.ai.transcriber import speech_transcriber
from app.ai.tts import tts_engine
from app.utils.audio_utils import save_upload_audio_file


PRESET_LIVE_CALLS = {
    "⚡ Electricity Live Call (Anna Nagar - Power Outage)": {
        "caller": "+919840112233",
        "district": "Chennai",
        "spoken": "TNEB helpline ah? Anna Nagar 4th main road la transformer blast aagi current illa 3 days ah. Romba hot ah irukku, seekiram repair pannunga.",
        "category": "Electricity",
        "lang": "tanglish"
    },
    "💧 Water Supply Emergency (Madurai - Contamination)": {
        "caller": "+919876543210",
        "district": "Madurai",
        "spoken": "குடிநீர் வாரியம்: எங்கள் பகுதியில் கடந்த 3 நாட்களாக சாக்கடை நீர் குடிநீருடன் கலந்து வருகிறது. குழந்தைகள் குடிக்க முடியவில்லை, உடனடியாக நடவடிக்கை எடுக்கவும்.",
        "category": "Water",
        "lang": "tamil"
    },
    "🚔 Police SOS Call (T Nagar - Emergency Incident)": {
        "caller": "+919840998877",
        "district": "Chennai",
        "spoken": "100 Police Control Room? T Nagar Ranganathan Street la chain snatching nadanthurukku. Urgent ah patrol police anupunga please!",
        "category": "Police",
        "lang": "tanglish"
    },
    "🧹 Municipal Health Call (Fairlands - Drain Overflow)": {
        "caller": "+919123456789",
        "district": "Salem",
        "spoken": "Corporation 1913: Fairlands bus stand kitta kuppai thotti nirambi rottula kottikittu irukku. Mosquitoes romba adhigam, drainage block aayiduchi.",
        "category": "Sanitation",
        "lang": "tanglish"
    },
    "🛣️ Highways Road Hazard (Gandhipuram - Deep Potholes)": {
        "caller": "+919444123456",
        "district": "Coimbatore",
        "spoken": "Highways department: Severe road cave-in and dangerous potholes near Gandhipuram signal. Two-wheelers are skidding. Please fix urgently.",
        "category": "Roads",
        "lang": "english"
    }
}


def render_live_phone_agent(lang: str = "en"):
    """
    Renders the dedicated Live Mobile Phone Call & Conversational AI Voice Agent Dashboard.
    """
    is_ta = (lang == "ta")

    # Hero Banner
    st.markdown(f"""
    <div class="tn-header-banner" style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 58, 138, 0.9) 100%); border-left: 6px solid #10b981;">
        <div>
            <h1 class="tn-header-title">📱 Live Phone Call & AI Voice Dashboard</h1>
            <div class="tn-header-subtitle">
                {"உங்கள் மொபைல் போனை இணைத்து AI குரல் அதிகாரியுடன் நேரடியாக பேசுங்கள்" if is_ta else "Connect Your Mobile Phone & Converse Directly with the Tamil Nadu AI Voice Officer"}
            </div>
        </div>
        <div style="text-align: right;">
            <span style="background: rgba(16, 185, 129, 0.2); color: #34d399; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.85rem; border: 1px solid #10b981;">
                LIVE TELEPHONY HUD
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Top Status Bar
    st_col1, st_col2, st_col3, st_col4 = st.columns(4)
    with st_col1:
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid #38bdf8; border-radius: 10px; padding: 12px;">
            <div style="color: #94a3b8; font-size: 0.72rem; text-transform: uppercase;">🇮🇳 Exotel Virtual Number</div>
            <div style="color: #38bdf8; font-size: 1.1rem; font-weight: 800; font-family: monospace; margin-top: 2px;">
                {settings.EXOTEL_CALLER_ID or "08088919888"}
            </div>
            <div style="color: #64748b; font-size: 0.7rem;">Inbound / Outbound Ready</div>
        </div>
        """, unsafe_allow_html=True)
    with st_col2:
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid #10b981; border-radius: 10px; padding: 12px;">
            <div style="color: #94a3b8; font-size: 0.72rem; text-transform: uppercase;">📞 State Toll-Free Number</div>
            <div style="color: #ffd700; font-size: 1.1rem; font-weight: 800; font-family: monospace; margin-top: 2px;">
                1800-425-VOXEN
            </div>
            <div style="color: #64748b; font-size: 0.7rem;">1800-425-8693 (24x7 Free)</div>
        </div>
        """, unsafe_allow_html=True)
    with st_col3:
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid #a855f7; border-radius: 10px; padding: 12px;">
            <div style="color: #94a3b8; font-size: 0.72rem; text-transform: uppercase;">🤖 Speech AI Engine</div>
            <div style="color: #c084fc; font-size: 1.1rem; font-weight: 800; margin-top: 2px;">
                OpenAI Whisper + gTTS
            </div>
            <div style="color: #64748b; font-size: 0.7rem;">Tamil • English • Tanglish</div>
        </div>
        """, unsafe_allow_html=True)
    with st_col4:
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid #f59e0b; border-radius: 10px; padding: 12px;">
            <div style="color: #94a3b8; font-size: 0.72rem; text-transform: uppercase;">💬 Instant SMS Gateway</div>
            <div style="color: #fbbf24; font-size: 1.1rem; font-weight: 800; margin-top: 2px;">
                Exotel REST API / Twilio
            </div>
            <div style="color: #64748b; font-size: 0.7rem;">Live Dispatch Enabled</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Main Grid: Left = Call Dialer & Mic, Right = Live AI Call HUD & Stream
    call_col_left, call_col_right = st.columns([1.1, 1.4])

    with call_col_left:
        st.markdown("### 📞 1. Phone Connection & Audio Stream")

        conn_mode = st.radio(
            "Select How You Want to Talk with AI:",
            [
                "🎙️ Speak via Live Microphone (Browser Voice Call)",
                "📲 Connect Real Mobile Phone (Exotel Outbound Call / Toll-Free)",
                "📋 Standard Audio Call Presets"
            ],
            key="live_phone_mode"
        )

        user_mobile = st.text_input(
            "Citizen Mobile Number (உங்கள் தொலைபேசி எண்):",
            value="+919840112233",
            key="live_phone_user_num"
        )

        spoken_message = ""
        uploaded_audio_path = None

        if "Speak via Live Microphone" in conn_mode:
            st.markdown("""
            <div style="background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; padding: 10px; border-radius: 6px; margin: 10px 0;">
                <b>🎙️ Microphone Active:</b> Click the record button below, speak your grievance in Tamil, English, or Tanglish, and press stop.
            </div>
            """, unsafe_allow_html=True)

            mic_audio = st.audio_input("Speak Grievance to AI Officer", key="live_agent_mic")
            if mic_audio is not None:
                audio_bytes = mic_audio.read()
                uploaded_audio_path = save_upload_audio_file(audio_bytes, f"live_call_{user_mobile[-6:]}.wav")
                st.audio(audio_bytes, format="audio/wav")

                with st.spinner("🤖 Transcribing speech with Whisper AI in real-time..."):
                    trans_res = speech_transcriber.transcribe(uploaded_audio_path)
                    spoken_message = trans_res.get("text", "")
                    st.success(f"**Transcribed Speech:** \"{spoken_message}\"")

        elif "Connect Real Mobile Phone" in conn_mode:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(30, 58, 138, 0.5) 0%, rgba(15, 23, 42, 0.8) 100%); border: 1px solid #3b82f6; border-radius: 10px; padding: 16px; margin: 10px 0;">
                <h4 style="color: #ffd700; margin-top: 0;">📲 Option A: Dial Directly from Your Phone</h4>
                <div style="color: #e2e8f0; font-size: 0.95rem;">
                    Dial either of these numbers from your mobile handset:
                </div>
                <div style="margin: 8px 0;">
                    • <b>Exotel Virtual Number:</b> <code style="font-size: 1.1rem; color: #38bdf8;">{settings.EXOTEL_CALLER_ID or "08088919888"}</code><br>
                    • <b>TN Toll-Free:</b> <code style="font-size: 1.1rem; color: #ffd700;">1800-425-8693</code>
                </div>
                <div style="color: #94a3b8; font-size: 0.8rem;">
                    The IVR will answer in Tamil & English, record your message, run Whisper AI, and send you a tracking SMS.
                </div>
                <hr style="border-color: rgba(255,255,255,0.1); margin: 12px 0;">
                <h4 style="color: #34d399; margin-top: 0;">📞 Option B: Click-to-Call (AI Dials Your Phone)</h4>
                <div style="color: #cbd5e1; font-size: 0.85rem; margin-bottom: 8px;">
                    Click below and our Exotel/Twilio telephony server will initiate an outbound call to <b>{user_mobile}</b>.
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("📲 Initiate Outbound Call to My Phone (Exotel API)", type="primary", use_container_width=True):
                with st.spinner(f"Connecting telecom call to {user_mobile} via Exotel Cloud Gateway..."):
                    call_res = telephony_service.initiate_outbound_call(to_phone=user_mobile)
                    if call_res.get("call_mode") == "LIVE_EXOTEL_CARRIER":
                        st.success(f"📞 {call_res['message']}")
                        st.info(f"**Call SID:** `{call_res['call_sid']}` | **Gateway Mode:** `LIVE_EXOTEL_CARRIER`")
                    else:
                        st.warning(f"⚠️ **Carrier Notice ({call_res.get('call_mode')})**: The telecom carrier could not place a live call to your phone.")
                        if call_res.get("carrier_error"):
                            st.caption(f"**Carrier Error:** `{call_res['carrier_error']}`")
                        st.info("💡 **Recommended Option:** Select **🎙️ Speak via Live Microphone** above to converse directly with the Tamil Nadu AI Voice Agent through your browser without requiring telecom balance!")

            scenario_choice = st.selectbox("Or choose a live test message for the call:", list(PRESET_LIVE_CALLS.keys()))
            spoken_message = PRESET_LIVE_CALLS[scenario_choice]["spoken"]

        else:
            scenario_choice = st.selectbox("Choose Standard Call Scenario Preset:", list(PRESET_LIVE_CALLS.keys()))
            preset_data = PRESET_LIVE_CALLS[scenario_choice]
            user_mobile = preset_data["caller"]
            spoken_message = st.text_area("Spoken Grievance Audio Transcript:", value=preset_data["spoken"], height=120)

        # Trigger Call Button
        call_btn = st.button("🚀 Start Live AI Voice Call & Process Grievance", type="primary", use_container_width=True)

    with call_col_right:
        st.markdown("### 🤖 2. Live Conversation Stream & AI Voice Agent")

        if call_btn:
            if not spoken_message or len(spoken_message.strip()) < 3:
                st.error("❌ Please record speech or enter a grievance message first.")
            else:
                # Visual Phone Call HUD Simulation
                with st.spinner("📞 Connecting call... AI Officer listening & transcribing speech..."):
                    db = SessionLocal()
                    try:
                        # Process Call via Telephony Service
                        result = telephony_service.process_call_recording(
                            db=db,
                            caller_phone=user_mobile.strip(),
                            local_audio_path=uploaded_audio_path,
                            transcription_hint=spoken_message.strip()
                        )

                        # Update transcript if explicit message
                        from app.models.complaint import Complaint
                        complaint = db.query(Complaint).filter(Complaint.id == result["complaint_id"]).first()
                        if complaint:
                            complaint.original_message = spoken_message.strip()
                            complaint.transcribed_text = spoken_message.strip()
                            db.commit()

                        # Build spoken AI Voice response (Tamil & English)
                        spoken_dialogue = tts_engine.build_caller_conversation(
                            complaint_id=result["complaint_id"],
                            category=result["category"],
                            priority=result["priority"],
                            department_name_ta=result.get("department", "தமிழ்நாடு அரசு துறை"),
                            department_name_en=result.get("department", "Government of Tamil Nadu Department"),
                            lang="ta" if result.get("language") in ["ta", "tamil", "tanglish"] else "en"
                        )

                        # Dispatch outbound confirmation SMS
                        sms_res = sms_service.send_complaint_confirmation_sms(
                            phone_number=user_mobile.strip(),
                            complaint_id=result["complaint_id"],
                            category=result["category"],
                            priority=result["priority"],
                            department_name=result.get("department", "TN Government"),
                            language=result.get("language", "tamil")
                        )

                    finally:
                        db.close()

                # Call Connected Animation & Card
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(15, 23, 42, 0.95) 100%); border: 2px solid #10b981; border-radius: 12px; padding: 18px; margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-size: 1.8rem;">🟢</span>
                            <div>
                                <div style="color: #34d399; font-weight: 800; font-size: 1.15rem;">CALL ACTIVE: AI Public Grievance Officer</div>
                                <div style="color: #94a3b8; font-size: 0.8rem;">Connected with Caller: <code style="color: #ffd700;">{user_mobile}</code></div>
                            </div>
                        </div>
                        <span style="background: #10b981; color: #022c22; padding: 4px 12px; border-radius: 20px; font-weight: 800; font-size: 0.8rem;">
                            LIVE SPEECH SESSION
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Dialogue Speech Bubbles
                st.markdown("#### 💬 Live Conversation Transcript:")

                # 1. Citizen Bubble
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-start; margin-bottom: 12px;">
                    <div style="background: rgba(30, 41, 59, 0.9); border: 1px solid #475569; border-radius: 12px 12px 12px 2px; padding: 12px 16px; max-width: 85%;">
                        <div style="color: #38bdf8; font-size: 0.75rem; font-weight: 700; margin-bottom: 4px;">👤 CITIZEN CALLER ({user_mobile})</div>
                        <div style="color: #f1f5f9; font-size: 0.95rem; line-height: 1.5;">"{spoken_message}"</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 2. AI Officer Spoken Bubble
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin-bottom: 12px;">
                    <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.25) 0%, rgba(15, 23, 42, 0.95) 100%); border: 1px solid #10b981; border-radius: 12px 12px 2px 12px; padding: 12px 16px; max-width: 85%;">
                        <div style="color: #34d399; font-size: 0.75rem; font-weight: 700; margin-bottom: 4px;">🤖 AI VOICE OFFICER (SPOKEN AUDIO STREAM)</div>
                        <div style="color: #f8fafc; font-size: 0.95rem; line-height: 1.5;">"{spoken_dialogue['active_script']}"</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Voice Audio Player for AI Speaking back
                if spoken_dialogue.get("audio_bytes"):
                    st.markdown("##### 🔊 Listen to AI Officer Voice Audio Talking to Caller:")
                    st.audio(spoken_dialogue["audio_bytes"], format="audio/mp3")

                # Action Result Breakdown
                st.markdown("---")
                st.markdown("#### 🎫 Generated Grievance Ticket & Auto-Triage:")

                t_c1, t_c2 = st.columns(2)
                with t_c1:
                    st.markdown(f"""
                    <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid #3b82f6; border-radius: 8px; padding: 12px;">
                        <div><b>Ticket ID:</b> <code style="color: #ffd700; font-size: 1.1rem;">{result['complaint_id']}</code></div>
                        <div><b>Category:</b> {result['category']}</div>
                        <div><b>Priority:</b> <span style="color: {'#ef4444' if result['priority'] == 'Emergency' else '#f97316'}; font-weight: 700;">{result['priority']}</span></div>
                        <div><b>Assigned Department:</b> {result['department']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with t_c2:
                    st.markdown(f"""
                    <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid #10b981; border-radius: 8px; padding: 12px;">
                        <div style="color: #34d399; font-weight: 700;">📱 Instant Confirmation SMS Dispatched</div>
                        <div style="color: #cbd5e1; font-size: 0.8rem; margin-top: 4px;">
                            Recipient: <b>{user_mobile}</b><br>
                            Status: <span style="color: #34d399;">Delivered ({sms_res.get('delivery_mode', 'MOCK_SIMULATED')})</span>
                        </div>
                        <div style="background: rgba(0,0,0,0.3); border-radius: 4px; padding: 6px; font-family: monospace; font-size: 0.72rem; color: #94a3b8; margin-top: 6px; white-space: pre-line;">
                            {sms_res.get('message', '')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        else:
            # Standby Screen
            st.markdown("""
            <div style="background: rgba(15, 23, 42, 0.6); border: 2px dashed #475569; border-radius: 12px; padding: 40px; text-align: center;">
                <div style="font-size: 3rem; margin-bottom: 10px;">🎙️📞</div>
                <h3 style="color: #cbd5e1; margin: 0;">AI Voice Agent Standby</h3>
                <p style="color: #94a3b8; max-width: 480px; margin: 10px auto;">
                    Select your input method on the left panel (Microphone, Real Phone Dialing, or Preset), then click <b>Start Live AI Voice Call</b> to begin the conversation.
                </p>
            </div>
            """, unsafe_allow_html=True)
