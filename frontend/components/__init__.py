from frontend.components.styles import inject_custom_styles
from frontend.components.citizen_portal import render_citizen_portal
from frontend.components.officer_dashboard import render_officer_dashboard
from frontend.components.telephony_simulator import render_telephony_simulator
from frontend.components.live_map import render_live_grievance_map, render_single_ticket_live_map

__all__ = [
    "inject_custom_styles",
    "render_citizen_portal",
    "render_officer_dashboard",
    "render_telephony_simulator",
    "render_live_grievance_map",
    "render_single_ticket_live_map",
]
