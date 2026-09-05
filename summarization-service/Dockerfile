FROM python:3.14-slim AS builder

WORKDIR /app

ENV POETRY_VIRTUALENVS_IN_PROJECT=1

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --only main --no-root


FROM python:3.14-slim

LABEL authors="gomode13"
LABEL description="Task Tracker summarization service"

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY russian_trusted_root_ca.cer ./

ENV PATH="/app/.venv/bin:$PATH"

RUN useradd --create-home appuser
USER appuser

CMD ["python", "-m", "app.main"]