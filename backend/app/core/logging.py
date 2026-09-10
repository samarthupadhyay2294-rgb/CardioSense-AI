import logging
import sys
from pathlib import Path

from app.core.config import settings


def setup_logging():
    log_level = logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO
    
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    handlers = [
        logging.StreamHandler(sys.stdout),
    ]
    
    if settings.ENVIRONMENT == "development":
        log_dir = Path(__file__).parent.parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        handlers.append(logging.FileHandler(log_dir / "app.log"))
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
    )
    
    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("uvicorn.access").setLevel(log_level)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


logger = logging.getLogger(__name__)