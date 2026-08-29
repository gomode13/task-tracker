import logging
from uuid import UUID

import time
from confluent_kafka import Consumer, KafkaException

from app.config import settings
from app.email_sender.tasks import send_daily_report_email
from app.scheduler.schemas import DailyReportRecipient, DailyReportResponse

logger = logging.getLogger(__name__)

config = {
    "bootstrap.servers": settings.kafka_bootstrap_servers,
    "group.id": "task-tracker-scheduler",
    "auto.offset.reset": "earliest",
}


def consume_daily_report_responses(users_by_request_id: dict[UUID, DailyReportRecipient]) -> None:
    consumer = Consumer(config)
    consumer.subscribe(["daily-report-responses"])

    try:
        started_at = time.monotonic()
        while True:
            msg = consumer.poll(timeout=1.0)

            if time.monotonic() - started_at > settings.DAILY_REPORT_RESPONSE_TIMEOUT_SECONDS:
                logger.warning(
                    "Timed out waiting for daily report responses: %s pending, waited %s seconds",
                    len(users_by_request_id),
                    settings.DAILY_REPORT_RESPONSE_TIMEOUT_SECONDS,
                )
                break

            if msg is None:
                continue

            if msg.error():
                logger.error("Unexpected error with Kafka Consumer: %s", msg.error())
                raise KafkaException(msg.error())

            response = DailyReportResponse.model_validate_json(msg.value().decode("utf-8"))
            logger.info("Received daily report response: offset=%s, request_id=%s", msg.offset(), response.request_id)

            if response.request_id not in users_by_request_id:
                continue

            recipient = users_by_request_id.pop(response.request_id)
            send_daily_report_email.delay(
                recipient.email, recipient.completed_titles, recipient.pending_titles, response.summary
            )

            if not users_by_request_id:
                break

        for recipient in users_by_request_id.values():
            send_daily_report_email.delay(recipient.email, recipient.completed_titles, recipient.pending_titles, None)

    finally:
        consumer.close()
