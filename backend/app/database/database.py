from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.database.models import ECGAnalysis
    Base.metadata.create_all(bind=engine)
    _migrate_sqlite()

def _migrate_sqlite():
    """Add columns added after the initial schema without resetting data."""
    if not settings.DATABASE_URL.startswith("sqlite"):
        return
    import sqlalchemy as sa
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    columns = {c["name"] for c in inspector.get_columns("ecg_analyses")}
    additions = {
        "analysis_type": "VARCHAR(20) NOT NULL DEFAULT 'signal'",
        "model_name": "VARCHAR(100)",
        "image_path": "VARCHAR(500)",
        "gradcam_path": "VARCHAR(500)",
        "gradcam_available": "INTEGER",
    }
    with engine.begin() as conn:
        for name, definition in additions.items():
            if name not in columns:
                conn.execute(text(f"ALTER TABLE ecg_analyses ADD COLUMN {name} {definition}"))