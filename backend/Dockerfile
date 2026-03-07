FROM alpine:3.23 AS mozjpeg
RUN apk --no-cache add cmake nasm make gcc g++ musl-dev curl && \
    curl -L https://github.com/mozilla/mozjpeg/archive/refs/tags/v4.1.1.tar.gz | tar xz -C /tmp && \
    cd /tmp/mozjpeg-4.1.1 && \
    cmake -G"Unix Makefiles" \
      -DBUILD_SHARED_LIBS=FALSE \
      -DPNG_SUPPORTED=FALSE \
      -DWITH_TURBOJPEG=FALSE \
      -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
      . && \
    make -j$(nproc)

FROM ghcr.io/astral-sh/uv:bookworm-slim

COPY --from=mozjpeg /tmp/mozjpeg-4.1.1/cjpeg-static /usr/local/bin/cjpeg

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

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
CMD ["sh", "-c", "uv run _setup.py && uv run manage.py collectstatic --noinput && uv run granian --interface wsgi project.wsgi:application --host 0.0.0.0 --workers 4"]
