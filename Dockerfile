# Use the offical Golang image to create a build artifact.
# This is based on Debian and sets the GOPATH to /go.
# https://hub.docker.com/_/golang
FROM redis as redis-server

FROM python:3.7.4

# Copy local code to the container image.
WORKDIR /iredis
COPY . .

RUN pip install poetry && poetry install

COPY --from=redis-server /usr/local/bin/redis-server /redis-server

# Run the web service on container startup.
CMD ["iredis"]
