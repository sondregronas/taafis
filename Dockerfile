# ===== Stage 1: Builder =====
FROM python:3.10-slim AS builder

# Setup timezone and basic tools
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ='Europe/Oslo'

RUN apt-get update && apt-get install -y \
        tzdata \
        build-essential \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Upgrade pip and install build dependencies
RUN pip install --upgrade pip setuptools wheel

# Copy local project files and build wheels
WORKDIR /taafis
COPY requirements.txt /taafis
RUN pip wheel --wheel-dir=/wheels -r requirements.txt

# ===== Stage 2: Alpine runtime =====
FROM python:3.10-alpine

# Install runtime dependencies
RUN apk add --no-cache tzdata

# Set timezone and secrets
ENV TZ='Europe/Oslo'
ENV WEBHOOK_SECRET='secret'

# Copy wheels and project files from builder
COPY --from=builder /wheels /wheels
COPY --from=builder /taafis /taafis
WORKDIR /taafis

# Install dependencies from wheels
RUN pip install --no-index --find-links=/wheels -r requirements.txt

# Expose port and run the app directly
EXPOSE 8000
CMD ["python", "app.py"]
