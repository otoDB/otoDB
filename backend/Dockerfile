FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev curl build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://d2lang.com/install.sh | sh -s --

COPY pyproject.toml ./

RUN pip install --upgrade pip
RUN pip install . && pip install psycopg2-binary

COPY . .

EXPOSE 8000
