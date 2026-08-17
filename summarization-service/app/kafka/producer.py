import logging

from aiokafka import AIOKafkaProducer

from app.config import settings
from app.schemas import DailyReportResponse

logger = logging.getLogger(__name__)


async def send_one_daily_report_response(response: DailyReportResponse) -> None:
    producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap_servers)
    await producer.start()
    try:
        await producer.send_and_wait("daily-report-responses", response.model_dump_json().encode("utf-8"))
        logger.info("Sent daily report response: request_id=%s", response.request_id)
    finally:
        await producer.stop()
