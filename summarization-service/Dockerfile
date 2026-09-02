FROM python:3.14-slim

LABEL authors="gomode13"
LABEL description="Task Tracker summarization service"

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry

ENV POETRY_VIRTUALENVS_IN_PROJECT=1

RUN poetry install --only main --no-root

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY russian_trusted_root_ca.cer ./

ENV PATH="/app/.venv/bin:$PATH"

RUN useradd --create-home appuser
USER appuser

CMD ["python", "-m", "app.main"]