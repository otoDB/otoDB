FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev curl build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./

RUN pip install --upgrade pip
RUN pip install .
RUN pip install psycopg[binary]

COPY . .

EXPOSE 8000
CMD ["sh", "-c", "python _setup.py && python manage.py collectstatic --noinput && granian --interface wsgi project.wsgi:application --host 0.0.0.0"]
