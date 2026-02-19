FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=main_docker.py

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY main_docker.py .
COPY auth.py .
COPY models.py .
COPY views.py .
COPY db_names.py .
COPY reid_blueprint.py .
COPY minio_config.py .
COPY main.py .
COPY config.py .

COPY static ./static
COPY templates ./templates
COPY sync ./sync

# Create instance directory for database (will be mounted as volume)
RUN mkdir -p /app/instance

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 3139

CMD ["gunicorn", "--bind", "0.0.0.0:3139", "--workers", "2", "--timeout", "300", "--preload", "main_docker:app"]
