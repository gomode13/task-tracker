import logging

from confluent_kafka import KafkaError, Message, Producer

from app.config import settings
from app.scheduler.schemas import DailyReportRequest

logger = logging.getLogger(__name__)

producer = Producer({"bootstrap.servers": settings.kafka_bootstrap_servers})


def delivery_report(err: KafkaError | None, msg: Message) -> None:
    if err is not None:
        logger.error("Failed to deliver message: %s", err)
    else:
        logger.info("Delivered message: %s", msg.value())


def send_daily_report_request(request: DailyReportRequest) -> None:
    message = request.model_dump_json().encode("utf-8")
    producer.produce(topic="daily-report-requests", value=message, on_delivery=delivery_report)
