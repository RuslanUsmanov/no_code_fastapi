FROM python:3.12-slim as builder

WORKDIR /app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app/wheels /wheels

COPY . /app

RUN pip install --no-cache /wheels/*

CMD bash -c "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"
