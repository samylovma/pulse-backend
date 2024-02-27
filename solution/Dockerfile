FROM python:3.12.2-alpine3.19

WORKDIR /app

RUN python -m venv ./venv

COPY requirements.txt .
RUN ./venv/bin/pip install -r requirements.txt

COPY pyproject.toml .
COPY src src
RUN ./venv/bin/pip install .

ENV SERVER_ADDRESS=0.0.0.0:8080

CMD exec ./venv/bin/gunicorn -b=$SERVER_ADDRESS 'pulse_backend:create_app()'
