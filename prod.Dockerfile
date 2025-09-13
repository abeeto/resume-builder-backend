# Multi-stage build for PROD
FROM python:3.13-slim as builder

# ENV for Build stage
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VENV_IN_PROJECT=1
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create true \
    && poetry install --only=main --no-root \
    && rm -rf $POETRY_CACHE_DIR

# PROD stage
FROM python:3.13-slim as production

# ENV for PROD stage
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=your_project.settings.production

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge -y --auto-remove

# Create non-root user for security
RUN groupadd -r django && useradd --no-log-init -r -g django django

WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# to use venv
ENV PATH="/app/.venv/bin:$PATH"

COPY --chown=django:django . .

USER django

EXPOSE 8000

WORKDIR /app/resume-builder-django
CMD ["gunicorn", "-c", "gunicorn.conf.py", "your_project.wsgi:application"]