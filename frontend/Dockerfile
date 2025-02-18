# https://bun.sh/guides/ecosystem/docker

# Stage 1: Set up the base image
# FROM oven/bun:latest AS base
# FROM oven/bun:latest
FROM node:22-alpine AS install
WORKDIR /app

# Stage 2: Install all dependencies (for development)
# FROM base AS install
# RUN mkdir -p /temp/dev
# COPY package.json bun.lock /temp/dev/
# RUN cd /temp/dev && bun install --frozen-lockfile
COPY package.json .
RUN npm install

# Stage 3: Install production dependencies (exclude devDependencies)
# RUN mkdir -p /temp/prod
# COPY package.json bun.lock /temp/prod/
# RUN cd /temp/prod && bun install --frozen-lockfile --production

# Stage 4: Copy source code, run tests, and build the application
# FROM base AS prerelease
# COPY --from=install /temp/dev/node_modules node_modules
COPY . .
# ENV NODE_ENV=production

ARG OTODB_FRONTEND_DOMAIN
ENV OTODB_FRONTEND_DOMAIN=${OTODB_FRONTEND_DOMAIN}
ENV PUBLIC_BACKEND_URL_EXTERNAL=https://${OTODB_FRONTEND_DOMAIN}/
ENV PUBLIC_BACKEND_URL_INTERNAL=http://backend:8000/

RUN npm run prepare
RUN npm run build

# Stage 5: Create the final release image
# FROM base AS release
# COPY --from=install /temp/prod/node_modules node_modules

# TODO: Shouldn't need to copy the entire source code, but copying build only doesn't work...?
# COPY --from=prerelease /usr/src/app .

FROM oven/bun:latest AS build
WORKDIR /app

COPY --from=install /app/build .

USER bun
EXPOSE 5173/tcp

ENTRYPOINT [ "sh", "-c", "ORIGIN=https://$OTODB_FRONTEND_DOMAIN HOST=0.0.0.0 PORT=5173 bun run start" ]
