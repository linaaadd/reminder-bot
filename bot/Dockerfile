FROM python:3.12-slim

# ffmpeg powers the STT transcode fallback (.oga/opus → mp3).
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run DB migrations, then launch bot + API in one process.
CMD ["sh", "-c", "alembic upgrade head && python -m app.main"]
