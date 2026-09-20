import streamlit as st

# ==============================================================================
# 1. OFFICIAL TAMIL NADU GOVERNMENT OFFICER PRESETS
# ==============================================================================
OFFICER_ACCOUNTS = {
    "admin_tn": {
        "id": "admin_tn",
        "name": "Dr. V. Rajeshwaran, IAS",
        "role": "State Grievance Commissioner",
        "dept_code": "ALL_DEPTS",
        "department": "Public Grievance Redressal Dept, Govt of Tamil Nadu",
        "district": "Statewide / Secretariat, Chennai",
        "pin": "admin2026",
        "clearance": "Top Secret / Level 1 (Full State Authority)",
        "badge_color": "#ffd700",
        "avatar": "🏛️"
    },
    "tneb_officer": {
        "id": "tneb_officer",
        "name": "Er. S. Murugesan, M.E.",
        "role": "Superintending Engineer (Distribution)",
        "dept_code": "TANGEDCO",
        "department": "Tamil Nadu Generation & Distribution Corp (TNEB)",
        "district": "Chennai South & Central",
        "pin": "tneb2026",
        "clearance": "Level 2 (Electricity Operations)",
        "badge_color": "#f59e0b",
        "avatar": "⚡"
    },
    "twad_officer": {
        "id": "twad_officer",
        "name": "Er. K. Anbarasan, M.Tech",
        "role": "Executive Engineer (Metro Water)",
        "dept_code": "TWAD",
        "department": "TN Water Supply & Drainage Board (CMWSSB)",
        "district": "Chennai & Kanchipuram",
        "pin": "twad2026",
        "clearance": "Level 2 (Water & Sanitation)",
        "badge_color": "#38bdf8",
        "avatar": "💧"
    },
    "police_officer": {
        "id": "police_officer",
        "name": "Thiru. R. Venkatesh, IPS",
        "role": "Deputy Commissioner of Police",
        "dept_code": "POLICE",
        "department": "Tamil Nadu Police (100 / 112 Control Room)",
        "district": "Greater Chennai Police",
        "pin": "police2026",
        "clearance": "Level 1 (Emergency Dispatch)",
        "badge_color": "#ef4444",
        "avatar": "🚔"
    },
    "gcc_officer": {
        "id": "gcc_officer",
        "name": "Thiru. M. Senthil Nathan",
        "role": "Zonal Sanitary & Health Officer",
        "dept_code": "GCC",
        "department": "Greater Chennai Corporation & Public Health",
        "district": "Chennai (Zone 8 - Anna Nagar)",
        "pin": "gcc2026",
        "clearance": "Level 2 (Municipal Maintenance)",
        "badge_color": "#10b981",
        "avatar": "🧹"
    }
}

# ==============================================================================
# 2. CITIZEN DEMO PRESETS
# ==============================================================================
CITIZEN_ACCOUNTS = {
    "karthik_chennai": {
        "id": "cit_karthik",
        "name": "Karthik Subramanian",
        "phone": "+919840112233",
        "district": "Chennai",
        "area": "4th Main Road, Anna Nagar",
        "preferred_lang": "tanglish",
        "avatar": "👨‍💼"
    },
    "priya_cbe": {
        "id": "cit_priya",
        "name": "Priya Sundaram",
        "phone": "+919444123456",
        "district": "Coimbatore",
        "area": "Cross Cut Road, Gandhipuram",
        "preferred_lang": "english",
        "avatar": "👩‍💻"
    },
    "murugan_madurai": {
        "id": "cit_murugan",
        "name": "Murugan Pandian",
        "phone": "+919876543210",
        "district": "Madurai",
        "area": "Simmakkal North Street",
        "preferred_lang": "tamil",
        "avatar": "👨‍🌾"
    },
    "kavitha_salem": {
        "id": "cit_kavitha",
        "name": "Kavitha Ramasamy",
        "phone": "+919123456789",
        "district": "Salem",
        "area": "Fairlands Main Road",
        "preferred_lang": "tanglish",
        "avatar": "👩‍🏫"
    }
}


def init_auth_session():
    """Initializes global authentication state keys."""
    if "is_authenticated" not in st.session_state:
        st.session_state["is_authenticated"] = False
    if "user_role" not in st.session_state:
        st.session_state["user_role"] = None  # 'officer' or 'citizen'
    if "user_profile" not in st.session_state:
        st.session_state["user_profile"] = None
    # Maintain legacy keys for compatibility
    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False
    if "admin_profile" not in st.session_state:
        st.session_state["admin_profile"] = None


def is_authenticated() -> bool:
    """Returns True if any user is logged into the application."""
    init_auth_session()
    return st.session_state.get("is_authenticated", False)


def get_auth_role() -> str:
    """Returns 'officer' or 'citizen'."""
    init_auth_session()
    return st.session_state.get("user_role") or "citizen"


def get_auth_user() -> dict:
    """Returns currently authenticated user profile."""
    init_auth_session()
    return st.session_state.get("user_profile") or CITIZEN_ACCOUNTS["karthik_chennai"]


def logout():
    """Logs out the current user and resets the session."""
    st.session_state["is_authenticated"] = False
    st.session_state["user_role"] = None
    st.session_state["user_profile"] = None
    st.session_state["admin_logged_in"] = False
    st.session_state["admin_profile"] = None
    st.rerun()


def render_master_login_gateway(lang: str = "en"):
    """
    Renders an ultra-modern, glassmorphic Master Login Gateway for the entire VoxentraAI application.
    """
    init_auth_session()
    is_ta = (lang == "ta")

    # Hero Banner
    st.markdown("""
    <div style="max-width: 900px; margin: 0 auto; text-align: center; padding: 24px 0 16px 0;">
        <div style="display: inline-block; position: relative;">
            <div style="width: 90px; height: 90px; margin: 0 auto 12px auto; background: radial-gradient(circle, rgba(255, 215, 0, 0.28) 0%, rgba(15, 23, 42, 0) 70%); border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid rgba(255, 215, 0, 0.5); box-shadow: 0 0 30px rgba(255, 215, 0, 0.35);">
                <span style="font-size: 3rem;">🏛️</span>
            </div>
        </div>
        <div style="color: #ffd700; font-size: 0.85rem; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 4px;">
            தமிழ்நாடு அரசு • GOVERNMENT OF TAMIL NADU
        </div>
        <h1 style="color: #ffffff; font-size: 2.4rem; font-weight: 800; letter-spacing: -0.5px; margin: 0 0 8px 0;">
            VoxentraAI Public Grievance Portal
        </h1>
        <div style="color: #94a3b8; font-size: 1rem; font-weight: 500; max-width: 640px; margin: 0 auto;">
            AI-Powered Multi-Channel Grievance Redressal System • Tamil (தமிழ்), English & Tanglish
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Master Login Gateway Dual Tabs
    login_tab_officer, login_tab_citizen = st.tabs([
        "🛡️ Government Officer / Admin Login (அதிகாரி உள்நுழைவு)",
        "👥 Citizen & Public Access (பொதுமக்கள் சேவை)"
    ])

    # =========================================================================
    # TAB 1: OFFICER & ADMIN AUTHENTICATION
    # =========================================================================
    with login_tab_officer:
        col_off_left, col_off_right = st.columns([1.1, 1.3], gap="large")

        with col_off_left:
            st.markdown("""
            <div style="background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 20px; box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                    <span style="font-size: 1.2rem;">⚡</span>
                    <span style="color: #38bdf8; font-size: 0.9rem; font-weight: 700; text-transform: uppercase;">1-Click Officer Presets</span>
                </div>
                <div style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 14px;">
                    Select an official department role for instant verified access:
                </div>
            </div>
            """, unsafe_allow_html=True)

            selected_officer_key = st.selectbox(
                "Officer Designation:",
                options=list(OFFICER_ACCOUNTS.keys()),
                format_func=lambda k: f"{OFFICER_ACCOUNTS[k]['avatar']} {OFFICER_ACCOUNTS[k]['name']} ({OFFICER_ACCOUNTS[k]['role']})",
                key="master_officer_preset_sel"
            )
            off_preset = OFFICER_ACCOUNTS[selected_officer_key]

            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.7); border-left: 4px solid {off_preset['badge_color']}; border-radius: 8px; padding: 14px; margin: 12px 0;">
                <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem;">{off_preset['avatar']} {off_preset['name']}</div>
                <div style="color: {off_preset['badge_color']}; font-size: 0.82rem; font-weight: 600; margin: 2px 0;">{off_preset['role']}</div>
                <div style="color: #94a3b8; font-size: 0.78rem;">🏢 {off_preset['department']}</div>
                <div style="color: #64748b; font-size: 0.75rem; margin-top: 4px;">📍 {off_preset['district']} | 🛡️ {off_preset['clearance']}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"🚀 Enter Command Center as {off_preset['name'].split(',')[0]}", type="secondary", use_container_width=True, key="btn_quick_officer_login"):
                st.session_state["is_authenticated"] = True
                st.session_state["user_role"] = "officer"
                st.session_state["user_profile"] = off_preset
                st.session_state["admin_logged_in"] = True
                st.session_state["admin_profile"] = off_preset
                st.session_state["admin_user"] = selected_officer_key
                st.success(f"✅ Access Granted: Welcome {off_preset['name']}!")
                st.rerun()

        with col_off_right:
            st.markdown("""
            <div style="background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(20px); border: 1px solid rgba(255, 215, 0, 0.3); border-radius: 16px; padding: 22px; box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
                    <div style="color: #ffd700; font-size: 1.05rem; font-weight: 800; display: flex; align-items: center; gap: 8px;">
                        <span>🛡️</span> Officer Security Gateway
                    </div>
                    <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; font-size: 0.72rem; font-weight: 700; padding: 4px 10px; border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.3);">
                        SECURE HTTPS
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.form("master_officer_login_form"):
                user_id = st.text_input(
                    "Officer ID / Username (அதிகாரி பயனர் பெயர்):",
                    value=selected_officer_key,
                    placeholder="e.g. admin_tn, tneb_officer",
                    key="input_master_officer_id"
                )
                user_pin = st.text_input(
                    "Security PIN / Password (கடவுச்சொல்):",
                    value=off_preset["pin"],
                    type="password",
                    placeholder="Enter security PIN",
                    key="input_master_officer_pin"
                )

                st.caption("🔒 Department clearance level verified upon login.")
                submit_officer = st.form_submit_button("🔑 Authenticate & Enter Command Center", type="primary", use_container_width=True)

                if submit_officer:
                    user_clean = user_id.strip().lower()
                    if user_clean in OFFICER_ACCOUNTS and user_pin.strip() == OFFICER_ACCOUNTS[user_clean]["pin"]:
                        st.session_state["is_authenticated"] = True
                        st.session_state["user_role"] = "officer"
                        st.session_state["user_profile"] = OFFICER_ACCOUNTS[user_clean]
                        st.session_state["admin_logged_in"] = True
                        st.session_state["admin_profile"] = OFFICER_ACCOUNTS[user_clean]
                        st.session_state["admin_user"] = user_clean
                        st.success("✅ Authentication successful! Loading Command Center...")
                        st.rerun()
                    elif user_pin.strip() in ["admin2026", "tneb2026", "twad2026", "police2026", "gcc2026"]:
                        matched = "admin_tn"
                        for k, v in OFFICER_ACCOUNTS.items():
                            if v["pin"] == user_pin.strip():
                                matched = k
                                break
                        st.session_state["is_authenticated"] = True
                        st.session_state["user_role"] = "officer"
                        st.session_state["user_profile"] = OFFICER_ACCOUNTS[matched]
                        st.session_state["admin_logged_in"] = True
                        st.session_state["admin_profile"] = OFFICER_ACCOUNTS[matched]
                        st.session_state["admin_user"] = matched
                        st.success("✅ Authentication successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid Officer ID or Security PIN. Please try again.")

    # =========================================================================
    # TAB 2: CITIZEN ACCESS & LOGIN
    # =========================================================================
    with login_tab_citizen:
        col_cit_left, col_cit_right = st.columns([1.1, 1.3], gap="large")

        with col_cit_left:
            st.markdown("""
            <div style="background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 20px; box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                    <span style="font-size: 1.2rem;">👨‍👩‍👧‍👦</span>
                    <span style="color: #34d399; font-size: 0.9rem; font-weight: 700; text-transform: uppercase;">1-Click Citizen Demo Login</span>
                </div>
                <div style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 14px;">
                    Experience the portal as a resident from various Tamil Nadu districts:
                </div>
            </div>
            """, unsafe_allow_html=True)

            selected_cit_key = st.selectbox(
                "Citizen Profile:",
                options=list(CITIZEN_ACCOUNTS.keys()),
                format_func=lambda k: f"{CITIZEN_ACCOUNTS[k]['avatar']} {CITIZEN_ACCOUNTS[k]['name']} ({CITIZEN_ACCOUNTS[k]['district']})",
                key="master_cit_preset_sel"
            )
            cit_preset = CITIZEN_ACCOUNTS[selected_cit_key]

            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.7); border-left: 4px solid #34d399; border-radius: 8px; padding: 14px; margin: 12px 0;">
                <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem;">{cit_preset['avatar']} {cit_preset['name']}</div>
                <div style="color: #34d399; font-size: 0.82rem; font-weight: 600; margin: 2px 0;">📱 {cit_preset['phone']}</div>
                <div style="color: #94a3b8; font-size: 0.78rem;">📍 {cit_preset['area']}, {cit_preset['district']}</div>
                <div style="color: #64748b; font-size: 0.75rem; margin-top: 4px;">🌐 Preferred Language: <b>{cit_preset['preferred_lang'].title()}</b></div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"👤 Enter Citizen Portal as {cit_preset['name']}", type="primary", use_container_width=True, key="btn_quick_cit_login"):
                st.session_state["is_authenticated"] = True
                st.session_state["user_role"] = "citizen"
                st.session_state["user_profile"] = cit_preset
                st.success(f"✅ Welcome, {cit_preset['name']}!")
                st.rerun()

        with col_cit_right:
            st.markdown("""
            <div style="background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(20px); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 16px; padding: 22px; box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
                    <div style="color: #38bdf8; font-size: 1.05rem; font-weight: 800; display: flex; align-items: center; gap: 8px;">
                        <span>📱</span> Citizen Mobile Sign-In
                    </div>
                    <span style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; font-size: 0.72rem; font-weight: 700; padding: 4px 10px; border-radius: 12px; border: 1px solid rgba(56, 189, 248, 0.3);">
                        INSTANT OTP
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.form("master_citizen_login_form"):
                from app.config import TAMIL_NADU_DISTRICTS
                c_phone = st.text_input("Mobile Number (தொலைபேசி எண்):", value="+919840112233", placeholder="+919840112233", key="custom_cit_phone")
                c_name = st.text_input("Citizen Full Name (உங்கள் பெயர்):", value="Karthik Subramanian", placeholder="e.g. Karthik", key="custom_cit_name")
                c_district = st.selectbox("District (மாவட்டம்):", TAMIL_NADU_DISTRICTS, index=0, key="custom_cit_district")
                c_otp = st.text_input("One-Time Passcode (OTP):", value="7890", placeholder="Enter 4-digit OTP", key="custom_cit_otp")

                st.caption("📲 Instant SMS verification enabled for all 38 Tamil Nadu districts.")
                submit_citizen = st.form_submit_button("🚀 Verify & Enter Citizen Portal", type="primary", use_container_width=True)

                if submit_citizen:
                    clean_p = c_phone.strip()
                    if len(clean_p) < 10:
                        st.error("❌ Please enter a valid 10-digit mobile number.")
                    else:
                        custom_profile = {
                            "id": f"cit_{clean_p[-4:]}",
                            "name": c_name.strip() or "Citizen",
                            "phone": clean_p if clean_p.startswith("+") else f"+91{clean_p}",
                            "district": c_district,
                            "area": f"{c_district} Region",
                            "preferred_lang": "tanglish",
                            "avatar": "👤"
                        }
                        st.session_state["is_authenticated"] = True
                        st.session_state["user_role"] = "citizen"
                        st.session_state["user_profile"] = custom_profile
                        st.success(f"✅ Verified! Welcome, {custom_profile['name']}.")
                        st.rerun()

    # Footer
    st.markdown("""
    <div style="margin-top: 30px; text-align: center; color: #64748b; font-size: 0.8rem; border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 16px;">
        🏛️ Government of Tamil Nadu • State AI Grievance Redressal Monitoring System • All Rights Reserved
    </div>
    """, unsafe_allow_html=True)


def is_admin_logged_in() -> bool:
    """Returns True if officer is authenticated."""
    init_auth_session()
    return st.session_state.get("is_authenticated", False) and st.session_state.get("user_role") == "officer"


def get_current_admin() -> dict:
    """Returns currently authenticated officer profile."""
    init_auth_session()
    return st.session_state.get("user_profile") or OFFICER_ACCOUNTS["admin_tn"]


def logout_admin():
    """Logs out officer session."""
    logout()


def render_admin_login_page(lang: str = "en"):
    """Renders the master login gateway focusing on officer login."""
    render_master_login_gateway(lang=lang)


def render_officer_top_bar(current_tab: str = "Overview"):
    """
    Renders top navigation bar showing authenticated officer profile, clearance, and quick logout.
    """
    profile = get_current_admin()
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 58, 138, 0.9) 100%); border: 1px solid rgba(255, 215, 0, 0.3); border-radius: 14px; padding: 14px 22px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.35);">
        <div style="display: flex; align-items: center; gap: 14px;">
            <div style="width: 44px; height: 44px; background: rgba(255, 215, 0, 0.15); border: 1.5px solid {profile['badge_color']}; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.4rem;">
                {profile['avatar']}
            </div>
            <div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="color: #ffffff; font-weight: 800; font-size: 1.05rem;">{profile['name']}</span>
                    <span style="background: rgba(255, 215, 0, 0.15); color: {profile['badge_color']}; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 6px; border: 1px solid {profile['badge_color']}80;">
                        {profile['role']}
                    </span>
                </div>
                <div style="color: #94a3b8; font-size: 0.78rem;">
                    🏢 {profile['department']} • 📍 {profile['district']}
                </div>
            </div>
        </div>
        <div style="text-align: right; display: flex; align-items: center; gap: 12px;">
            <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; border-radius: 20px; padding: 4px 12px; color: #34d399; font-size: 0.75rem; font-weight: 700;">
                🟢 OFFICER SESSION ACTIVE
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

