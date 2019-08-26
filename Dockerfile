FROM python:3

WORKDIR /iredis
COPY README.md poetry.lock pyproject.toml ./
COPY iredis ./iredis

RUN apt-get update && apt-get install -y --allow-unauthenticated \
    redis-server && \
    rm -rf /var/lib/apt/lists/*


RUN python3 -m venv iredis_env && \
    . iredis_env/bin/activate && \
    pip install poetry && \
    poetry install --no-dev && \
    rm -rf ~/.cache

CMD ["sh","-c","redis-server --daemonize yes && . iredis_env/bin/activate && iredis"]
