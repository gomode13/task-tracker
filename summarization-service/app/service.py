import httpx

from app.kafka.producer import kafka_producer
from app.llm.client import GigaChatClient
from app.schemas import DailyReportRequest, DailyReportResponse

llm_client = GigaChatClient()


async def handle_daily_report_request(request: DailyReportRequest) -> None:
    try:
        summary = await llm_client.generate_summary(
            request.report_date, request.completed_titles, request.pending_titles
        )
        response = DailyReportResponse(request_id=request.request_id, summary=summary)
    except httpx.HTTPError as e:
        response = DailyReportResponse(request_id=request.request_id, error=str(e))
    await kafka_producer.send_daily_report_response(response)
