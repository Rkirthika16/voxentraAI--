"""
VoxentraAI Live GIS Map Tracking & Spatial Analytics Component.
Renders interactive 3D spatial maps of Tamil Nadu public grievances, field teams, and citizen tracking.
"""
import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Optional, Dict, Any

from app.config import (
    TAMIL_NADU_DISTRICT_COORDS,
    get_district_coordinates,
    CATEGORIES,
    PRIORITY_LEVELS,
    STATUS_LEVELS
)
from app.database import SessionLocal
from app.services.complaint_service import complaint_service

CATEGORY_COLORS = {
    "Police": [239, 68, 68, 220],       # Red
    "Water": [56, 189, 248, 220],      # Blue/Cyan
    "Electricity": [245, 158, 11, 220], # Amber/Yellow
    "Roads": [249, 115, 22, 220],      # Orange
    "Sanitation": [16, 185, 129, 220], # Emerald Green
    "Other": [168, 85, 247, 220]       # Purple
}

PRIORITY_COLORS = {
    "Emergency": [239, 68, 68, 240],   # Red (Intense)
    "High": [249, 115, 22, 220],        # Orange
    "Medium": [59, 130, 246, 200],      # Blue
    "Low": [16, 185, 129, 180]          # Green
}

PRIORITY_HEX = {
    "Emergency": "#ef4444",
    "High": "#f97316",
    "Medium": "#3b82f6",
    "Low": "#10b981"
}


def render_live_grievance_map():
    """
    Renders the Full Tamil Nadu GIS Live Grievance Map with dual PyDeck 3D and Plotly OpenStreetMap engines.
    """
    st.markdown("""
    <div class="tn-header-banner">
        <div>
            <h1 class="tn-header-title">🗺️ Tamil Nadu Live GIS Grievance Map</h1>
            <div class="tn-header-subtitle">Real-Time Spatial Distribution, 3D Emergency SOS Clustering & District Triage</div>
        </div>
        <div style="text-align: right;">
            <span style="background: rgba(16, 185, 129, 0.2); color: #34d399; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.85rem; border: 1px solid #10b981;">
                🔴 LIVE SATELLITE FEED
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Filter Controls
    f1, f2, f3, f4 = st.columns([1.2, 1, 1, 1.2])
    with f1:
        map_view_mode = st.selectbox(
            "🛰️ GIS Engine View:",
            ["🌟 3D PyDeck Spatial Mesh (Recommended)", "🗺️ OpenStreetMap Scatter (2D)", "📊 Zonal Density Heatmap"],
            key="gis_view_mode"
        )
    with f2:
        filter_cat = st.selectbox("Filter Category:", ["All Categories"] + CATEGORIES, key="map_filter_cat")
    with f3:
        filter_prio = st.selectbox("Filter Priority:", ["All Priorities"] + PRIORITY_LEVELS, key="map_filter_prio")
    with f4:
        district_zoom = st.selectbox(
            "📍 Focus District:",
            ["All 38 Districts (Statewide)"] + list(TAMIL_NADU_DISTRICT_COORDS.keys()),
            key="map_district_focus"
        )

    db = SessionLocal()
    try:
        items, total = complaint_service.list_complaints(
            db=db,
            category=filter_cat if filter_cat != "All Categories" else None,
            priority=filter_prio if filter_prio != "All Priorities" else None,
            district=district_zoom if district_zoom != "All 38 Districts (Statewide)" else None,
            page_size=300
        )
    finally:
        db.close()

    if not items:
        st.warning("⚠️ No grievance records found matching the active filters.")
        return

    # Build DataFrame for Map
    map_rows = []
    for c in items:
        lat = c.latitude
        lon = c.longitude
        if not lat or not lon:
            lat, lon = get_district_coordinates(c.location_district)

        # Slight jitter for multiple items in same district center so they don't overlap completely
        import random
        jitter_lat = lat + random.uniform(-0.02, 0.02)
        jitter_lon = lon + random.uniform(-0.02, 0.02)

        prio_col = PRIORITY_COLORS.get(c.priority, [59, 130, 246, 200])
        cat_col = CATEGORY_COLORS.get(c.category, [168, 85, 247, 200])
        elev = 12000 if c.priority == "Emergency" else (7000 if c.priority == "High" else 3000)

        map_rows.append({
            "id": c.id,
            "category": c.category,
            "priority": c.priority,
            "status": c.status,
            "district": c.location_district or "Tamil Nadu",
            "locality": c.location_details or "General Area",
            "phone": c.citizen_phone,
            "department": c.department_code or "-",
            "message": c.original_message[:70] + "...",
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M"),
            "lat": jitter_lat,
            "lon": jitter_lon,
            "elevation": elev,
            "prio_color": prio_col,
            "cat_color": cat_col,
            "radius": 18000 if c.priority == "Emergency" else (12000 if c.priority == "High" else 8000)
        })

    df_map = pd.DataFrame(map_rows)

    # Determine center coordinates & zoom
    if district_zoom != "All 38 Districts (Statewide)" and district_zoom in TAMIL_NADU_DISTRICT_COORDS:
        center_lat, center_lon = get_district_coordinates(district_zoom)
        zoom_level = 10.5
    else:
        center_lat, center_lon = 10.8505, 78.7047
        zoom_level = 6.6

    # =========================================================================
    # RENDER SELECTED MAP ENGINE
    # =========================================================================
    if "3D PyDeck" in map_view_mode:
        # Layer 1: Scatterplot circles for incidents
        scatter_layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_map,
            get_position=["lon", "lat"],
            get_color="prio_color",
            get_radius="radius",
            pickable=True,
            opacity=0.85,
            stroked=True,
            filled=True,
            get_line_color=[255, 255, 255, 180],
            line_width_min_pixels=1
        )

        # Layer 2: 3D Column Elevation Layer
        column_layer = pdk.Layer(
            "ColumnLayer",
            data=df_map,
            get_position=["lon", "lat"],
            get_elevation="elevation",
            elevation_scale=1,
            radius=4000,
            get_fill_color="prio_color",
            pickable=True,
            auto_highlight=True,
        )

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=zoom_level,
            pitch=45 if "3D" in map_view_mode else 0,
            bearing=10
        )

        tooltip_spec = {
            "html": """
            <div style="background: rgba(15, 23, 42, 0.95); border: 1px solid #ffd700; border-radius: 8px; padding: 10px; color: white; font-family: sans-serif; font-size: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
                <div style="font-weight: bold; color: #ffd700; font-size: 13px;">{id}</div>
                <div style="color: #38bdf8; margin: 3px 0;"><b>{category}</b> | <span style="color: #ef4444;">{priority} Priority</span></div>
                <div>📍 {locality}, {district}</div>
                <div>🏢 Dept: {department} | Status: <b>{status}</b></div>
                <div style="color: #94a3b8; font-size: 10px; margin-top: 4px;">⏱️ {created_at}</div>
            </div>
            """,
            "style": {"color": "white"}
        }

        deck = pdk.Deck(
            layers=[scatter_layer, column_layer],
            initial_view_state=view_state,
            tooltip=tooltip_spec,
            map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
        )

        st.pydeck_chart(deck, use_container_width=True)

    elif "OpenStreetMap" in map_view_mode:
        fig = px.scatter_mapbox(
            df_map,
            lat="lat",
            lon="lon",
            color="priority",
            color_discrete_map=PRIORITY_HEX,
            hover_name="id",
            hover_data={
                "category": True,
                "priority": True,
                "status": True,
                "district": True,
                "locality": True,
                "department": True,
                "created_at": True,
                "lat": False,
                "lon": False
            },
            zoom=zoom_level,
            center={"lat": center_lat, "lon": center_lon},
            mapbox_style="open-street-map",
            title=f"Tamil Nadu Grievance Map ({len(df_map)} Incidents Plotted)"
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=30, b=0),
            height=550,
            legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.01, bgcolor="rgba(15, 23, 42, 0.85)")
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        # Zonal Heatmap View
        fig = px.density_mapbox(
            df_map,
            lat="lat",
            lon="lon",
            z="elevation",
            radius=25,
            center={"lat": center_lat, "lon": center_lon},
            zoom=zoom_level,
            mapbox_style="open-street-map",
            title="Grievance Density & Severity Heatmap"
        )
        fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=550)
        st.plotly_chart(fig, use_container_width=True)

    # Spatial Analytics KPI Summary
    st.markdown("### 📊 Spatial Grievance Insights & District Triage")
    m1, m2, m3 = st.columns(3)

    with m1:
        st.markdown("##### 📍 Top 5 Grievance Hotspot Districts")
        dist_counts = df_map["district"].value_counts().head(5)
        st.dataframe(dist_counts.rename("Complaints"), use_container_width=True)

    with m2:
        st.markdown("##### 🚨 Active Emergency SOS Severity")
        emergencies = df_map[df_map["priority"] == "Emergency"]
        st.metric(
            "Active Emergency SOS Pins",
            f"{len(emergencies)} Critical Hotspots",
            delta="Urgent Action Required" if len(emergencies) > 0 else "Normal Status",
            delta_color="inverse"
        )
        if len(emergencies) > 0:
            st.caption(f"Districts affected: {', '.join(emergencies['district'].unique())}")

    with m3:
        st.markdown("##### ⚡ Department Field Load Distribution")
        dept_counts = df_map["department"].value_counts().head(5)
        st.dataframe(dept_counts.rename("Assigned Tickets"), use_container_width=True)


def render_single_ticket_live_map(complaint):
    """Renders a focused GPS locator map for a specific complaint ticket."""
    lat = complaint.latitude
    lon = complaint.longitude
    if not lat or not lon:
        lat, lon = get_district_coordinates(complaint.location_district)

    field_team_lat = lat + 0.008
    field_team_lon = lon + 0.006

    ticket_df = pd.DataFrame([
        {
            "name": f"📍 Incident: {complaint.id}",
            "type": "Grievance Site",
            "lat": lat,
            "lon": lon,
            "color": [239, 68, 68, 240] if complaint.priority == "Emergency" else [59, 130, 246, 220],
            "radius": 100
        },
        {
            "name": f"🛡️ Field Depot ({complaint.department_code or 'TN Zonal'})",
            "type": "Zonal Response Unit",
            "lat": field_team_lat,
            "lon": field_team_lon,
            "color": [16, 185, 129, 240],
            "radius": 80
        }
    ])

    scatter = pdk.Layer(
        "ScatterplotLayer",
        data=ticket_df,
        get_position=["lon", "lat"],
        get_color="color",
        get_radius="radius",
        pickable=True,
        stroked=True,
        filled=True,
        get_line_color=[255, 255, 255, 220],
        line_width_min_pixels=2
    )

    view_state = pdk.ViewState(
        latitude=lat,
        longitude=lon,
        zoom=13,
        pitch=30
    )

    deck = pdk.Deck(
        layers=[scatter],
        initial_view_state=view_state,
        tooltip={"html": "<b>{name}</b><br>Type: {type}", "style": {"color": "white", "background": "rgba(15,23,42,0.9)", "padding": "8px"}},
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
    )

    st.pydeck_chart(deck, use_container_width=True)
