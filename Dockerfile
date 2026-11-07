# Railway Dockerfile for backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app
ARG GIT_SHA=unknown
ENV GIT_SHA=${GIT_SHA}

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code (excluding sensitive files)
COPY backend/ .
RUN rm -f firebase_service_account.json  # Remove if accidentally copied

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
