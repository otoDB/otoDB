FROM python:3.14-slim AS build

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --all-extras

ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates git patch curl unzip \
    && rm -rf /var/lib/apt/lists/*
ENV DENO_INSTALL=/usr/local
RUN curl -fsSL https://deno.land/install.sh | sh -s -- -y
RUN uv run p12y apply

RUN OTODB_SECRET_KEY= uv run manage.py collectstatic --noinput

FROM python:3.14-slim

WORKDIR /app

COPY --from=build /app /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GRANIAN_INTERFACE=wsgi \
    GRANIAN_HOST=0.0.0.0 \
    GRANIAN_PORT=8000 \
    GRANIAN_WORKERS=4

# Ensure cookies.txt exists so volume mount doesn't create a directory
RUN touch cookies.txt

EXPOSE 8000
CMD ["sh", "-c", "python _setup.py && exec granian project.wsgi:application"]
