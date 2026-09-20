"""
VoxentraAI - Tamil Nadu Grievance Redressal API
Root FastAPI Application Entrypoint for Cloud (Render / Railway / Fly.io) & Local Environments.
"""

import os
import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Ensure project root is in sys.path so modules under app/ are importable everywhere
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.config import settings, UPLOAD_DIR
from app.database import init_db, SessionLocal
from app.utils.seed_data import seed_sample_data
from app.api.v1.router import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("voxentra.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: Database initialization and seed data loading."""
    logger.info("Initializing VoxentraAI Database & Tamil Nadu Departments...")
    init_db()
    
    # Pre-seed realistic samples if database is fresh
    db = SessionLocal()
    try:
        count = seed_sample_data(db)
        if count > 0:
            logger.info(f"Successfully seeded {count} sample Tamil Nadu complaints.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
    finally:
        db.close()
        
    logger.info("VoxentraAI Backend is ready.")
    yield
    logger.info("VoxentraAI Backend shutting down.")


# Instantiate FastAPI Application
app = FastAPI(
    title="VoxentraAI - Tamil Nadu Grievance Redressal API",
    description=(
        "AI-powered public complaint registration and management system supporting "
        "Voice Calls, SMS, Audio Uploads, and Web Text in Tamil, English, and Tanglish."
    ),
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Enable CORS for Streamlit, web clients, and external webhooks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists and mount static files
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Mount static folder if it exists
STATIC_DIR = BASE_DIR / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include API v1 Master Router (/api/v1)
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/", tags=["Health"])
def root():
    """Root status and API overview."""
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "region": "Tamil Nadu, India",
        "version": "2.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "api_prefix": settings.API_PREFIX,
        "endpoints": {
            "text_complaint": f"{settings.API_PREFIX}/complaints/text",
            "voice_complaint": f"{settings.API_PREFIX}/complaints/voice",
            "track_complaint": f"{settings.API_PREFIX}/complaints/{{id}}",
            "dashboard_metrics": f"{settings.API_PREFIX}/analytics/dashboard-metrics",
            "exotel_incoming_call": f"{settings.API_PREFIX}/webhooks/exotel/voice/incoming",
            "exotel_recording_callback": f"{settings.API_PREFIX}/webhooks/exotel/voice/recording",
            "exotel_sms_incoming": f"{settings.API_PREFIX}/webhooks/exotel/sms/incoming"
        }
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint for Render, Kubernetes, and load balancers."""
    return {
        "status": "healthy",
        "database": "connected",
        "supported_languages": ["Tamil (தமிழ்)", "English", "Tanglish"],
        "supported_channels": ["voice_call", "sms", "web_text", "voice_upload"]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", settings.PORT))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"[LAUNCH] Starting FastAPI server on http://{host}:{port}")
    print(f"[DOCS] Interactive Swagger Docs: http://{host}:{port}/docs")
    uvicorn.run("main:app", host=host, port=port, reload=True)
