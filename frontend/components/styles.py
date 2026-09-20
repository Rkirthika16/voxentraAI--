import streamlit as st

def inject_custom_styles():
    """Injects high-end, modern CSS styling with Tamil Nadu Government motifs, glassmorphism, and neon accents."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&family=Noto+Sans+Tamil:wght@400;500;600;700;800&display=swap');

        :root {
            --tn-gold: #ffd700;
            --tn-gold-glow: rgba(255, 215, 0, 0.35);
            --tn-blue-dark: #0a192f;
            --tn-blue-mid: #0f3460;
            --tn-accent-cyan: #38bdf8;
            --tn-accent-emerald: #10b981;
            --tn-accent-rose: #f43f5e;
            --glass-bg: rgba(15, 23, 42, 0.75);
            --glass-border: rgba(255, 255, 255, 0.1);
        }

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', 'Outfit', 'Noto Sans Tamil', sans-serif;
            color: #f8fafc;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', 'Noto Sans Tamil', sans-serif;
            font-weight: 700;
            letter-spacing: -0.02em;
        }

        code, pre {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Top Header Banner */
        .tn-header-banner {
            background: linear-gradient(135deg, #0a192f 0%, #0f3460 50%, #16213e 100%);
            border: 1px solid rgba(255, 215, 0, 0.3);
            border-radius: 18px;
            padding: 24px 32px;
            margin-bottom: 24px;
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.45), 0 0 20px rgba(255, 215, 0, 0.08);
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: relative;
            overflow: hidden;
        }

        .tn-header-banner::before {
            content: "";
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at 20% 50%, rgba(255, 215, 0, 0.08) 0%, transparent 50%);
            pointer-events: none;
        }

        .tn-header-title {
            color: #ffffff;
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .tn-header-subtitle {
            color: #ffd700;
            font-size: 1.05rem;
            font-weight: 600;
            margin-top: 4px;
            letter-spacing: 0.2px;
        }

        /* Glassmorphic Metric Cards */
        .metric-card {
            background: rgba(15, 23, 42, 0.75);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 20px 22px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            overflow: hidden;
        }

        .metric-card:hover {
            transform: translateY(-4px);
            border-color: rgba(255, 215, 0, 0.4);
            box-shadow: 0 14px 40px rgba(0, 0, 0, 0.35), 0 0 15px rgba(255, 215, 0, 0.15);
        }

        .metric-value {
            font-size: 2.4rem;
            font-weight: 800;
            color: #ffffff;
            margin: 6px 0 2px 0;
            font-family: 'Outfit', sans-serif;
            letter-spacing: -0.5px;
        }

        .metric-label {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #94a3b8;
            font-weight: 700;
        }

        /* Nav Pills Navigation styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: rgba(15, 23, 42, 0.75);
            padding: 8px;
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 10px;
            padding: 10px 18px;
            font-weight: 700;
            color: #94a3b8;
            border: none !important;
            transition: all 0.2s ease;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%) !important;
            color: #ffffff !important;
            box-shadow: 0 4px 15px rgba(37, 99, 235, 0.35);
        }

        /* Priority Badges */
        .badge-emergency {
            background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);
            color: #ffffff;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 800;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            box-shadow: 0 0 14px rgba(239, 68, 68, 0.6);
            display: inline-block;
            animation: pulse-red 2s infinite;
        }

        @keyframes pulse-red {
            0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
            100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }

        .badge-high {
            background: linear-gradient(135deg, #f97316 0%, #c2410c 100%);
            color: #ffffff;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 700;
            display: inline-block;
        }

        .badge-medium {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: #ffffff;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
        }

        .badge-low {
            background: linear-gradient(135deg, #10b981 0%, #047857 100%);
            color: #ffffff;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
        }

        /* Status Badges */
        .status-badge {
            padding: 5px 14px;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 700;
            display: inline-block;
        }

        .status-pending {
            background: rgba(234, 179, 8, 0.2);
            color: #facc15;
            border: 1px solid rgba(234, 179, 8, 0.5);
        }

        .status-inprogress {
            background: rgba(59, 130, 246, 0.2);
            color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.5);
        }

        .status-resolved {
            background: rgba(16, 185, 129, 0.2);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.5);
        }

        .status-rejected {
            background: rgba(239, 68, 68, 0.2);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.5);
        }

        /* Timeline Items */
        .timeline-container {
            border-left: 2px solid #3b82f6;
            margin-left: 12px;
            padding-left: 20px;
            margin-top: 18px;
            margin-bottom: 18px;
        }

        .timeline-item {
            position: relative;
            margin-bottom: 22px;
        }

        .timeline-item::before {
            content: "";
            position: absolute;
            left: -27px;
            top: 4px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #ffd700;
            box-shadow: 0 0 10px #ffd700;
        }

        .timeline-time {
            font-size: 0.75rem;
            color: #94a3b8;
            margin-bottom: 2px;
            font-family: 'JetBrains Mono', monospace;
        }

        .timeline-title {
            font-size: 0.95rem;
            font-weight: 700;
            color: #f1f5f9;
        }

        .timeline-desc {
            font-size: 0.85rem;
            color: #cbd5e1;
            margin-top: 6px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.06);
            padding: 10px 14px;
            border-radius: 8px;
        }

        /* Modern Officer Ticket Cards */
        .officer-ticket-card {
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            padding: 16px 20px;
            margin-bottom: 14px;
            transition: all 0.2s ease;
        }

        .officer-ticket-card:hover {
            border-color: rgba(56, 189, 248, 0.4);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        }

        /* Streamlit Button Tweaks */
        .stButton>button {
            border-radius: 10px;
            font-weight: 700;
            letter-spacing: 0.3px;
            padding: 8px 20px;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        }

        /* Form Inputs & Selects */
        .stTextInput>div>div>input, .stSelectbox>div>div {
            border-radius: 10px !important;
            border-color: rgba(255, 255, 255, 0.15) !important;
            background: rgba(15, 23, 42, 0.8) !important;
        }

        /* Custom Scrollbars */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #0a192f;
        }
        ::-webkit-scrollbar-thumb {
            background: #334155;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #475569;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
