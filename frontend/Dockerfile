FROM denoland/deno:alpine AS base
WORKDIR /app

FROM base AS install
COPY package.json deno.lock ./
RUN deno install

COPY . .

ARG OTODB_HASH
ENV PUBLIC_OTODB_HASH=${OTODB_HASH}

RUN deno task sync-schema
RUN deno task prepare
RUN deno task build

FROM base AS build
COPY --from=install /app/build .

EXPOSE 5173/tcp

ENTRYPOINT [ "sh", "-c", "exec env PROTOCOL_HEADER=x-forwarded-proto HOST_HEADER=x-forwarded-host HOST=0.0.0.0 PORT=5173 deno run --allow-env --allow-read --allow-net ./index.js" ]
