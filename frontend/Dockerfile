FROM node:22-alpine AS base
WORKDIR /app

RUN corepack enable pnpm
COPY package.json .
RUN pnpm install

COPY . .

ARG OTODB_FRONTEND_DOMAIN
ENV OTODB_FRONTEND_DOMAIN=${OTODB_FRONTEND_DOMAIN}
ENV PUBLIC_BACKEND_URL_EXTERNAL=https://${OTODB_FRONTEND_DOMAIN}/
ENV PUBLIC_BACKEND_URL_INTERNAL=http://backend:8000/

RUN pnpm run prepare
RUN pnpm run build

FROM base AS build
WORKDIR /app
COPY --from=base /app/build .

EXPOSE 5173/tcp

ENTRYPOINT [ "sh", "-c", "PROTOCOL_HEADER=x-forwarded-proto HOST_HEADER=x-forwarded-host HOST=0.0.0.0 PORT=5173 node ./index.js" ]
