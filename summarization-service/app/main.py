import asyncio
import logging

from app.kafka.consumer import consume_daily_report_requests
from app.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

try:
    asyncio.run(consume_daily_report_requests())
except KeyboardInterrupt:
    logger.info("Summarization service stopped")
