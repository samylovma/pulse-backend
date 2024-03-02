#! /bin/sh

echo 'Running migrations...'
./venv/bin/litestar database upgrade --no-prompt

echo 'Running application...'
./venv/bin/litestar run --port=$SERVER_PORT --host=0.0.0.0
