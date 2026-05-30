FROM python:3.10-slim

# Fix debconf warnings
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install ffmpeg and build dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app

# Expose nothing; this is a background worker
CMD ["python3", "-m", "VISHALMUSIC"]
