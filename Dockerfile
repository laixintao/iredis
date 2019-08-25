FROM python:3

RUN apt-get update && apt-get install -y --allow-unauthenticated \
    redis-server && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /iredis
COPY poetry.lock pyproject.toml ./
COPY iredis ./iredis

RUN python3 -m venv iredis_env && \
    . iredis_env/bin/activate && \
    pip install poetry && \
    poetry install --no-dev && \
    rm -rf ~/.cache

COPY --from=redis-server /usr/local/bin/redis-server /redis-server

CMD ["sh","-c","redis-server --daemonize yes && . iredis_env/bin/activate && iredis"]
