# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Build stage: install Python dependencies
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build deps separately so Docker can cache this layer.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt


# ---------------------------------------------------------------------------
# Runtime stage: lean production image
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

# Non-root user for security.
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy installed packages from the builder stage.
COPY --from=builder /install /usr/local

# Copy application source.
COPY app/ ./app/

# Drop to non-root user.
USER appuser

EXPOSE 8000

# Structured JSON logs go to stdout where the orchestration platform captures them.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOG_LEVEL=INFO

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
