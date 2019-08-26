FROM python:3

WORKDIR /iredis
COPY README.md poetry.lock pyproject.toml ./
COPY iredis ./iredis

RUN python3 -m venv iredis_env && \
    . iredis_env/bin/activate && \
    pip install poetry && \
    poetry install --no-dev && \
    rm -rf ~/.cache

ENTRYPOINT ["iredis_env/bin/iredis"]
