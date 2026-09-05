FROM python:3.14-slim AS builder

WORKDIR /app

ENV POETRY_VIRTUALENVS_IN_PROJECT=1

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --only main --no-root


FROM python:3.14-slim

LABEL authors="gomode13"
LABEL description="Task Tracker backend"

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY app ./app
COPY alembic.ini ./

ENV PATH="/app/.venv/bin:$PATH"

RUN useradd --create-home appuser
RUN mkdir -p /var/lib/celery && chown appuser /var/lib/celery
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]