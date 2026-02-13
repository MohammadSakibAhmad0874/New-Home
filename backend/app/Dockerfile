# Use full Python image (not slim) to ensure all build tools (gcc, make, openssl, etc.) are present
FROM python:3.11

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Start fresh, just install libpq-dev for postgres
RUN apt-get update \
    && apt-get install -y libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Use shell form to allow variable expansion for PORT
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"
