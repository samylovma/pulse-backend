FROM python:3.12.2-alpine3.19

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV SERVER_ADDRESS=0.0.0.0:8080

CMD ["sh", "-c", "exec python3 -m gunicorn --bind=$SERVER_ADDRESS 'app:create_app()'"]
