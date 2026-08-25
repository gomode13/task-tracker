from uuid import UUID

import httpx
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import session_factory
from app.kafka.producer import kafka_producer
from app.llm.client import GigaChatClient
from app.models import ProcessedRequest
from app.schemas import DailyReportRequest, DailyReportResponse

llm_client = GigaChatClient()


async def is_request_processed(session: AsyncSession, request_id: UUID) -> bool:
    query = select(exists().where(ProcessedRequest.request_id == request_id))
    return await session.scalar(query) is True


async def create_processed_request(session: AsyncSession, request_id: UUID) -> None:
    processed_request = ProcessedRequest(request_id=request_id)
    session.add(processed_request)
    await session.commit()


async def handle_daily_report_request(request: DailyReportRequest) -> None:
    async with session_factory() as session:
        if await is_request_processed(session, request.request_id):
            return
    try:
        summary = await llm_client.generate_summary(request.completed_titles, request.pending_titles)
        response = DailyReportResponse(request_id=request.request_id, summary=summary)
    except (httpx.HTTPError, KeyError, IndexError) as e:
        response = DailyReportResponse(request_id=request.request_id, error=str(e))
    await kafka_producer.send_daily_report_response(response)
    async with session_factory() as session:
        await create_processed_request(session, request.request_id)
