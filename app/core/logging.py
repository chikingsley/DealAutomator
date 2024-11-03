import logging
from app.core.config import LOGGING_CONFIG

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

    # Apply any custom logging configuration
    if LOGGING_CONFIG:
        logging.config.dictConfig(LOGGING_CONFIG)

    return logging.getLogger(__name__)
