from datetime import date
from uuid import UUID

from pydantic import BaseModel


class DailyReportRequest(BaseModel):
    request_id: UUID
    report_date: date
    completed_titles: list[str]
    pending_titles: list[str]


class DailyReportResponse(BaseModel):
    request_id: UUID
    summary: str | None = None
    error: str | None = None
