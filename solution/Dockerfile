FROM python:3.12.2-alpine3.19

WORKDIR /app

RUN python -m venv ./venv

COPY requirements.txt .
RUN ./venv/bin/pip install --require-hashes --requirement requirements.txt

COPY pyproject.toml .
COPY src src
RUN ./venv/bin/pip install --no-deps .

ENV SERVER_PORT=8080

CMD exec ./venv/bin/litestar --app=pulse_backend:create_app run --port $SERVER_PORT --host 0.0.0.0
