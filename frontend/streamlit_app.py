import os
import sys
from pathlib import Path

# Robust root workspace directory resolution
_curr = Path(__file__).resolve()
BASE_DIR = _curr.parent.parent if _curr.parent.name == "frontend" else _curr.parent

# Ensure root directory is at index 0 of sys.path
if str(BASE_DIR) in sys.path:
    sys.path.remove(str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR))

import streamlit as st

# Auto-launch Streamlit if executed directly via 'python frontend/streamlit_app.py'
if not st.runtime.exists():
    import subprocess
    print("[LAUNCH] Starting VoxentraAI Streamlit Portal on http://localhost:8501 ...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(Path(__file__).resolve())])
    sys.exit(0)

from app.config import settings
from app.database import init_db, SessionLocal
from app.utils.seed_data import seed_sample_data
from frontend.components.styles import inject_custom_styles
from frontend.components.auth_gateway import (
    is_authenticated,
    get_auth_role,
    get_auth_user,
    logout,
    render_master_login_gateway
)
from frontend.components.citizen_portal import render_citizen_portal
from frontend.components.officer_dashboard import render_officer_dashboard
from frontend.components.telephony_simulator import render_telephony_simulator
from frontend.components.live_phone_agent import render_live_phone_agent
from frontend.components.live_map import render_live_grievance_map

# Streamlit Page Setup
st.set_page_config(
    page_title="VoxentraAI - Tamil Nadu Grievance Redressal",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database on load
@st.cache_resource
def bootstrap_app():
    init_db()
    db = SessionLocal()
    try:
        seed_sample_data(db)
    finally:
        db.close()

bootstrap_app()

# Inject CSS Styles
inject_custom_styles()

# ==============================================================================
# GLOBAL AUTHENTICATION GUARD
# ==============================================================================
if not is_authenticated():
    # Render Master Login Gateway as overall app entrypoint
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 12px 0 8px 0;">
            <div style="font-size: 2.4rem;">🏛️</div>
            <h2 style="margin: 0; color: #ffd700; font-size: 1.5rem; font-weight: 800; letter-spacing: -0.5px;">VoxentraAI</h2>
            <div style="font-size: 0.78rem; color: #94a3b8; font-weight: 600; letter-spacing: 0.5px;">GOVERNMENT OF TAMIL NADU</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        lang_choice = st.radio(
            "🌐 Language / மொழி:",
            ["English", "தமிழ் (Tamil)"],
            horizontal=True,
            key="login_gate_lang"
        )
        lang_code = "ta" if "தமிழ்" in lang_choice else "en"

        st.markdown("---")
        st.info("🔒 **Secure Gateway:** Please log in as an Officer or Citizen to access the system.")

    render_master_login_gateway(lang=lang_code)
    st.stop()

# ==============================================================================
# AUTHENTICATED USER SESSION & SIDEBAR NAVIGATION
# ==============================================================================
user_role = get_auth_role()
user_profile = get_auth_user()

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 12px 0 6px 0;">
        <div style="font-size: 2.2rem;">🏛️</div>
        <h2 style="margin: 0; color: #ffd700; font-size: 1.4rem; font-weight: 800; letter-spacing: -0.5px;">VoxentraAI</h2>
        <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 600; letter-spacing: 0.5px;">TAMIL NADU GRIEVANCE AI</div>
    </div>
    """, unsafe_allow_html=True)

    # Logged-In User Profile Card
    badge_bg = "rgba(255, 215, 0, 0.15)" if user_role == "officer" else "rgba(16, 185, 129, 0.15)"
    badge_border = "#ffd700" if user_role == "officer" else "#10b981"
    role_title = "GOVT OFFICER" if user_role == "officer" else "VERIFIED CITIZEN"

    st.markdown(f"""
    <div style="background: {badge_bg}; border: 1px solid {badge_border}; border-radius: 12px; padding: 12px; margin-bottom: 12px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.5rem;">{user_profile.get('avatar', '👤')}</span>
            <div style="overflow: hidden;">
                <div style="color: #ffffff; font-weight: 800; font-size: 0.9rem; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">
                    {user_profile.get('name', 'User')}
                </div>
                <div style="color: {badge_border}; font-size: 0.72rem; font-weight: 700; text-transform: uppercase;">
                    {user_profile.get('role', role_title)}
                </div>
                <div style="color: #94a3b8; font-size: 0.7rem;">
                    📍 {user_profile.get('district', 'Tamil Nadu')}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔒 Sign Out / Switch User", type="secondary", use_container_width=True, key="sidebar_logout_btn"):
        logout()

    st.markdown("---")

    # Language Switcher
    lang_choice = st.radio(
        "🌐 Language / மொழி:",
        ["English", "தமிழ் (Tamil)"],
        horizontal=True,
        key="app_lang_choice"
    )
    lang_code = "ta" if "தமிழ்" in lang_choice else "en"

    st.markdown("---")

    # Navigation Menu tailored by Role
    if user_role == "officer":
        nav_options = [
            "🛡️ Officer Command Center (அதிகாரி பிரிவு)",
            "🗺️ Live GIS Grievance Map (நேரடி வரைபடம்)",
            "📱 Live Mobile Call & AI Voice Agent (நேரடி உரையாடல்)",
            "🏛️ Citizen Grievance Portal (பொதுமக்கள் சேவை)",
            "📞 Exotel Telephony & SMS Simulator (தொலைபேசி)",
            "ℹ️ System Architecture & NLP Engine"
        ]
    else:
        nav_options = [
            "🏛️ Citizen Grievance Portal (பொதுமக்கள் குறை பதிவு)",
            "📱 Live Mobile Call & AI Voice Agent (நேரடி உரையாடல்)",
            "🗺️ Live GIS Grievance Map (நேரடி வரைபடம்)",
            "📞 Exotel Telephony & SMS Simulator (தொலைபேசி)",
            "🛡️ Officer Command Center (அதிகாரி பிரிவு)",
            "ℹ️ System Architecture & NLP Engine"
        ]
    
    selected_page = st.selectbox(
        "📌 Navigation:",
        nav_options,
        index=0
    )

    st.markdown("---")

    # Exotel Cloud Telephony Badge
    exo_status_color = "#10b981" if settings.EXOTEL_ACCOUNT_SID and not settings.EXOTEL_ACCOUNT_SID.startswith("your_") else "#38bdf8"
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(15, 23, 42, 0.9) 100%); border: 1px solid {exo_status_color}; border-radius: 10px; padding: 12px; margin-bottom: 12px;">
        <div style="color: #34d399; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">🇮🇳 Exotel Telephony Gateway</div>
        <div style="font-size: 1.1rem; font-weight: 800; color: #ffd700; margin: 4px 0;">
            Caller ID: {settings.EXOTEL_CALLER_ID or "08088919888"}
        </div>
        <div style="font-size: 0.75rem; color: #cbd5e1;">Virtual Line & Toll-Free 1800-425-VOXEN</div>
    </div>
    """, unsafe_allow_html=True)

    # 24x7 Citizen Helpline
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(30, 58, 138, 0.4) 0%, rgba(15, 23, 42, 0.7) 100%); border: 1px solid rgba(59, 130, 246, 0.5); border-radius: 10px; padding: 12px; margin-bottom: 12px;">
        <div style="color: #93c5fd; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">📞 24x7 Citizen Helpline</div>
        <div style="font-size: 1.15rem; font-weight: 800; color: #ffd700; margin: 4px 0;">
            1800-425-VOXEN
        </div>
        <div style="font-size: 0.75rem; color: #cbd5e1;">(1800-425-8693 • Toll-Free)</div>
    </div>
    """, unsafe_allow_html=True)

    # Live Backend Integration Status Card
    st.markdown("##### 🔌 Backend API Status")
    try:
        import requests
        h_resp = requests.get(f"http://127.0.0.1:8000/health", timeout=1)
        if h_resp.status_code == 200:
            st.markdown("""
            <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; border-radius: 8px; padding: 10px; font-size: 0.85rem;">
                <div style="color: #34d399; font-weight: 700;">🟢 FastAPI Backend: ONLINE</div>
                <div style="margin-top: 6px;"><a href="http://127.0.0.1:8000/docs" target="_blank" style="color: #60a5fa; text-decoration: none; font-weight: 600;">📖 Open Swagger Docs ↗</a></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="color: #facc15; font-size: 0.8rem;">🟡 Status {h_resp.status_code}</div>', unsafe_allow_html=True)
    except Exception:
        st.markdown("""
        <div style="background: rgba(234, 179, 8, 0.15); border: 1px solid #eab308; border-radius: 8px; padding: 10px; font-size: 0.85rem;">
            <div style="color: #facc15; font-weight: 700;">🟡 Standalone Local DB Mode</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("v2.0.0 | Government of Tamil Nadu • FastAPI • Whisper AI")

# ==============================================================================
# MAIN VIEW ROUTING
# ==============================================================================
if "Officer Command Center" in selected_page:
    render_officer_dashboard(lang=lang_code)

elif "Live Mobile Call" in selected_page:
    render_live_phone_agent(lang=lang_code)

elif "Citizen" in selected_page:
    render_citizen_portal(lang=lang_code)

elif "Live GIS Grievance Map" in selected_page:
    render_live_grievance_map()

elif "Telephony" in selected_page:
    render_telephony_simulator()

elif "Architecture" in selected_page:
    st.markdown("""
    <div class="tn-header-banner">
        <div>
            <h1 class="tn-header-title">ℹ️ System Architecture & AI Pipeline</h1>
            <div class="tn-header-subtitle">Multi-Channel Grievance Ingestion with Tamil, English & Tanglish NLP</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### 🏛️ VoxentraAI Overview
    **VoxentraAI** is an AI-powered public grievance registration and management system custom engineered for the Government of Tamil Nadu. It bridges the gap between citizens and municipal authorities by allowing citizens to lodge complaints in **Tamil (தமிழ்), English, and Tanglish** through **Voice Phone Calls, SMS, Audio Uploads, and Web Text**.

    ---

    ### ⚙️ Core Modules
    - **Speech-to-Text**: OpenAI Whisper AI engine for Tamil and English acoustics.
    - **Language Identification**: Real-time detection of Tamil unicode script, Tanglish phonetics, and English.
    - **Multi-Class NLP Categorization**: Automatic routing to TWAD (Water), TANGEDCO (Electricity), Highways (Roads), GCC (Sanitation), and Revenue (Disaster).
    - **Priority Severity Engine**: 4-tier triage (Emergency SOS, High, Medium, Low).
    - **38 Tamil Nadu Districts Extraction**: Accurate entity identification from 200+ local landmarks and taluks.
    """)
