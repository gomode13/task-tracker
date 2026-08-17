import logging

from app.logging_config import setup_logging

setup_logging()

logger = logging.getLogger(__name__)
logger.info("Summarization service started")
