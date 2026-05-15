FROM denoland/deno:debian AS base
WORKDIR /app
ENV DENO_DIR=/deno-dir

FROM base AS build
ARG OTODB_HASH
ENV PUBLIC_OTODB_HASH=${OTODB_HASH}

COPY package.json deno.lock ./
RUN deno install --frozen

COPY . .
COPY --from=backend openapi.json /app/openapi.json
RUN deno task sync-schema \
 && deno task prepare \
 && deno task build

FROM base AS runtime
ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=5173 \
    PROTOCOL_HEADER=x-forwarded-proto \
    HOST_HEADER=x-forwarded-host

COPY --from=build /app/.deno-deploy /app/package.json ./
RUN deno install --entrypoint ./server.ts

USER deno
EXPOSE 5173
ENTRYPOINT ["deno", "run", "--allow-env", "--allow-read", "--allow-net", "./server.ts"]