# ───────────── Stage 1: Builder ─────────────
FROM python:3.13.5-alpine3.21 AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build deps only needed to compile C extensions
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    postgresql-dev \
    build-base \
    openssl-dev

COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --prefer-binary -r requirements.txt

# ───────────── Stage 2: Final Runtime ─────────────
FROM python:3.13.5-alpine3.21

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Only runtime deps — no compilers, no headers
RUN apk add --no-cache \
    libpq \
    libffi \
    openssl

# Create non-root user
RUN adduser -D appuser

WORKDIR /app

# Copy site-packages and binaries
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy app code and set permissions
COPY --chown=appuser:appuser . .

# Make entrypoint executable
RUN chmod +x /app/entrypoint.prod.sh

USER appuser

EXPOSE 8000

CMD ["./entrypoint.prod.sh"]
