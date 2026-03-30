FROM python:3.11-slim

# Install compilation dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    libsystemd-dev \
    make \
    git \
    meson \
    jq \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir wheel build

WORKDIR /src

# Fix git ownership issue
RUN git config --global --add safe.directory /src
