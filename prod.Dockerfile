FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VENV_IN_PROJECT=0
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

# Install system dependencies (runtime only)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Create non-root user
RUN groupadd -r django && useradd --no-log-init -r -g django django

# Set work directory
WORKDIR /app

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Install dependencies globally (no venv needed in container)
RUN poetry config virtualenvs.create false \
    && poetry install --only=main --no-root \
    && rm -rf $POETRY_CACHE_DIR

# Remove build dependencies to reduce image size
RUN apt-get purge -y --auto-remove build-essential libpq-dev

# Copy project files
COPY --chown=django:django . .

# Switch to non-root user
USER django

# Expose port
EXPOSE 8000

# Change to Django project directory and start server
WORKDIR /app/resume-builder-django
CMD ["sh", "-c", "python manage.py migrate && gunicorn -c ../gunicorn.conf.py core.wsgi:application"]