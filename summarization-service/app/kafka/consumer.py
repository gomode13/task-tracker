import logging

from aiokafka import AIOKafkaConsumer
from app.config import settings

logger = logging.getLogger(__name__)


async def consume_daily_report_requests() -> None:
    consumer = AIOKafkaConsumer(
        "daily-report-requests", bootstrap_servers=settings.kafka_bootstrap_servers, group_id="summarization-service"
    )
    await consumer.start()
    try:
        async for msg in consumer:
            logger.info("Received message: offset=%s, value=%s", msg.offset, msg.value)
    finally:
        await consumer.stop()
