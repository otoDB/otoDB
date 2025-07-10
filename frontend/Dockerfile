FROM oven/bun AS base
WORKDIR /app

FROM base AS install
RUN mkdir -p /temp/dev
COPY package.json bun.lock /temp/dev/
RUN cd /temp/dev && bun install --frozen-lockfile

RUN mkdir -p /temp/prod
COPY package.json bun.lock /temp/prod/
RUN cd /temp/prod && bun install --frozen-lockfile --production

FROM base AS prerelease
COPY --from=install /temp/dev/node_modules node_modules
COPY . .

ARG OTODB_FRONTEND_DOMAIN
ENV OTODB_FRONTEND_DOMAIN=${OTODB_FRONTEND_DOMAIN}
ENV PUBLIC_BACKEND_URL_EXTERNAL=https://${OTODB_FRONTEND_DOMAIN}/
ENV PUBLIC_BACKEND_URL_INTERNAL=http://backend:8000/

RUN bun run prepare
RUN bun run build

FROM base AS build
COPY --from=install /temp/prod/node_modules node_modules
COPY --from=prerelease /app/build .

EXPOSE 5173/tcp

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 CMD curl -f http://localhost:5173/ || exit 1

ENTRYPOINT [ "sh", "-c", "PROTOCOL_HEADER=x-forwarded-proto HOST_HEADER=x-forwarded-host HOST=0.0.0.0 PORT=5173 bun ./" ]
