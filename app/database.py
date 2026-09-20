from sqlalchemy import create_engine

from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

Base = declarative_base()

def get_db():
    """FastAPI Dependency for obtaining a database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create all database tables and seed initial department metadata."""
    from app.models import citizen, department, complaint, history  # noqa: F401
    Base.metadata.create_all(bind=engine)
    
    # Auto-migrate SQLite schema if new columns are added
    with engine.connect() as conn:
        try:
            from sqlalchemy import text
            res = conn.execute(text("PRAGMA table_info(complaints)")).fetchall()
            existing_cols = [row[1] for row in res]
            if existing_cols and "latitude" not in existing_cols:
                conn.execute(text("ALTER TABLE complaints ADD COLUMN latitude FLOAT"))
            if existing_cols and "longitude" not in existing_cols:
                conn.execute(text("ALTER TABLE complaints ADD COLUMN longitude FLOAT"))
            if existing_cols and "call_sid" not in existing_cols:
                conn.execute(text("ALTER TABLE complaints ADD COLUMN call_sid VARCHAR(100)"))
            if existing_cols and "recording_reference" not in existing_cols:
                conn.execute(text("ALTER TABLE complaints ADD COLUMN recording_reference VARCHAR(500)"))
            conn.commit()
        except Exception as e:
            pass
    
    # Initialize default departments if not present
    db = SessionLocal()
    try:
        from app.models.department import Department
        from app.config import TAMIL_NADU_DEPARTMENTS
        
        for dept_data in TAMIL_NADU_DEPARTMENTS:
            existing = db.query(Department).filter(Department.code == dept_data["code"]).first()
            if not existing:
                dept = Department(
                    code=dept_data["code"],
                    name_en=dept_data["name_en"],
                    name_ta=dept_data["name_ta"],
                    category=dept_data["category"],
                    contact_email=dept_data["contact_email"],
                    helpline_number=dept_data["helpline_number"]
                )
                db.add(dept)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error seeding default departments: {e}")
    finally:
        db.close()
