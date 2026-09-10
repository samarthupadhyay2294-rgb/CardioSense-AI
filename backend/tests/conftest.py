import os
import sys
import tempfile

os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(tempfile.gettempdir(), 'cardiosense_test.db')}"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from app.core.config import settings
settings.DATABASE_URL = os.environ["DATABASE_URL"]

from app.database.database import engine, Base, SessionLocal, init_db
from app.database.models import ECGAnalysis

init_db()


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
