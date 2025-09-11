FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_HOME=/app \
    FLASK_ENV=production \
    PORT=8000

WORKDIR ${APP_HOME}

# System deps
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements early for caching
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt && pip install gunicorn

# Copy app
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser ${APP_HOME}
USER appuser

# Ensure runtime directories
RUN mkdir -p /app/instance
RUN mkdir -p instance static/uploads

EXPOSE ${PORT}

ENV SQLALCHEMY_DATABASE_URI="sqlite:///instance/mariokart_tournament.db" \
    UPLOAD_FOLDER="static/uploads"

CMD exec gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 4 --timeout 120 app:app
