import logging

from aiokafka import AIOKafkaProducer

from app.config import settings
from app.schemas import DailyReportResponse

logger = logging.getLogger(__name__)


class KafkaProducerClient:
    def __init__(self, bootstrap_servers: str) -> None:
        self.bootstrap_servers = bootstrap_servers
        self.producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        if self.producer is None:
            self.producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
            await self.producer.start()

    async def stop(self) -> None:
        if self.producer is not None:
            await self.producer.stop()
            self.producer = None

    async def send_daily_report_response(self, response: DailyReportResponse) -> None:
        if self.producer is None:
            raise RuntimeError("Kafka producer is not started")

        await self.producer.send_and_wait("daily-report-responses", response.model_dump_json().encode("utf-8"))
        logger.info("Sent daily report response: request_id=%s", response.request_id)


kafka_producer = KafkaProducerClient(bootstrap_servers=settings.kafka_bootstrap_servers)
