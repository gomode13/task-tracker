import asyncio
import logging

from app.kafka.consumer import consume_daily_report_requests
from app.logging_config import setup_logging

setup_logging()

logger = logging.getLogger(__name__)

logger.info("Summarization service started")
asyncio.run(consume_daily_report_requests())
