from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ProcessedRequest(Base):
    __tablename__ = "processed_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[UUID] = mapped_column(unique=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
