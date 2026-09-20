import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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
    
    # Pre-seed realistic samples
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

app = FastAPI(
    title="VoxentraAI - Tamil Nadu Grievance Redressal API",
    description="AI-powered public complaint registration and management system supporting Voice Calls, SMS, Audio Uploads, and Web Text in Tamil, English, and Tanglish.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for Streamlit and frontend apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded voice recordings
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Include API v1 Router
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "region": "Tamil Nadu, India",
        "version": "1.0.0",
        "docs_url": "/docs",
        "api_prefix": settings.API_PREFIX
    }

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "supported_languages": ["Tamil (தமிழ்)", "English", "Tanglish"],
        "supported_channels": ["voice_call", "sms", "web_text", "voice_upload"]
    }

if __name__ == "__main__":
    import uvicorn
    print(f"[LAUNCH] Starting FastAPI server on http://{settings.HOST}:{settings.PORT}")
    print(f"[DOCS] Interactive Swagger Docs: http://{settings.HOST}:{settings.PORT}/docs")
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
