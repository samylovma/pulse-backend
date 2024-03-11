FROM python:3.12.2-alpine3.19 as builder

RUN pip install -U pip setuptools wheel && pip install pdm

WORKDIR /app

COPY pyproject.toml pdm.lock .
COPY src src

RUN pdm sync --prod --no-editable


FROM python:3.12.2-alpine3.19

WORKDIR /app

COPY --from=builder /app .
COPY migrations migrations

ENV LITESTAR_APP=pulse_backend:create_app
ENV SERVER_PORT=8080

COPY run.sh .
RUN chmod +x ./run.sh
CMD ["./run.sh"]
