FROM ghcr.io/astral-sh/uv:bookworm-slim


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --all-extras

ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

RUN apt-get update && apt-get install -y ca-certificates git patch curl unzip
ENV DENO_INSTALL=/usr/local
RUN curl -fsSL https://deno.land/install.sh | sh -s -- -y
RUN uv run p12y apply

# Ensure cookies.txt exists so volume mount doesn't create a directory
RUN touch cookies.txt

EXPOSE 8000
CMD ["sh", "-c", "python _setup.py && python manage.py collectstatic --noinput && exec granian --interface wsgi project.wsgi:application --host 0.0.0.0 --workers 4"]
