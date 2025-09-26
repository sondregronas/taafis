# ===== Stage 1: Builder =====
FROM python:3.10-slim AS builder

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ='Europe/Oslo'

RUN apt-get update && apt-get install -y \
        tzdata \
        build-essential \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip install --upgrade pip setuptools wheel

WORKDIR /taafis

COPY requirements.txt /taafis
RUN pip wheel --wheel-dir=/wheels -r requirements.txt

# ===== Stage 2: Debian-slim runtime =====
FROM python:3.10-slim

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y tzdata \
    && rm -rf /var/lib/apt/lists/*

ENV TZ='Europe/Oslo'
ENV WEBHOOK_SECRET='secret'

WORKDIR /taafis
COPY --from=builder /taafis /taafis
COPY --from=builder /wheels /wheels

RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-index --find-links=/wheels -r requirements.txt

COPY . /taafis

EXPOSE 8000
CMD ["python", "app.py"]
