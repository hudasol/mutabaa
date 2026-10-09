# Reproducible build and test image. No network needed after the image is built, except `verify-live`.
FROM python:3.13-slim AS base
RUN apt-get update && apt-get install -y --no-install-recommends nodejs npm make git && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.lock pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.lock
COPY . .
RUN pip install --no-cache-dir --no-deps -e . && cd site && npm ci
CMD ["make", "reproduce"]
