import logging

from aiokafka import AIOKafkaConsumer

from app.config import settings
from app.kafka.producer import kafka_producer
from app.schemas import DailyReportRequest
from app.service import handle_daily_report_request

logger = logging.getLogger(__name__)


async def consume_daily_report_requests() -> None:
    consumer = AIOKafkaConsumer(
        "daily-report-requests", bootstrap_servers=settings.kafka_bootstrap_servers, group_id="summarization-service"
    )
    await consumer.start()
    try:
        await kafka_producer.start()
        logger.info("Summarization service started")
        async for msg in consumer:
            try:
                request = DailyReportRequest.model_validate_json(msg.value.decode("utf-8"))
                logger.info("Received daily report request: offset=%s, request_id=%s", msg.offset, request.request_id)
                await handle_daily_report_request(request)
            except Exception:
                logger.exception("Error while handling daily report request")
    finally:
        await consumer.stop()
        await kafka_producer.stop()
