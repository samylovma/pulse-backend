FROM python:3.12.2-alpine3.19

WORKDIR /app

RUN python -m venv ./venv

COPY requirements.txt .
RUN ./venv/bin/pip install --require-hashes --requirement=requirements.txt

COPY pyproject.toml .
COPY src src
RUN ./venv/bin/pip install --no-deps .

COPY migrations migrations

ENV LITESTAR_APP=pulse_backend:create_app
ENV SERVER_PORT=8080

COPY run.sh .
RUN chmod +x ./run.sh
CMD ["./run.sh"]
