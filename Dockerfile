FROM golang:1.19-alpine AS builder

# Move to working directory (/build).
WORKDIR /build

# Copy and download dependency using go mod.
COPY go.mod go.sum ./
RUN go mod download

# Copy the code into the container.
COPY . .

# Set necessary environment variables needed for our image and build the API server.
ENV CGO_ENABLED=0 GOOS=linux GOARCH=amd64
RUN go build -ldflags="-s -w" -o dhcpserver .

FROM python:3.9

# Setup env
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONUNBUFFERED=1

# Install pipenv and compilation dependencies
RUN pip install pipenv

RUN apt-get update && apt-get install -y --no-install-recommends gcc \
        net-tools \
        bash \
        curl \
        wget \
        vim

# Copy binary and config files from /build to root folder of scratch container.
COPY --from=builder ["/build/dhcpserver", "/"]

ENTRYPOINT ["/dhcpserver", "-v"]
