# https://bun.sh/guides/ecosystem/docker

# Stage 1: Set up the base image
FROM oven/bun:1 AS base
WORKDIR /usr/src/app

# Stage 2: Install all dependencies (for development)
FROM base AS install
RUN mkdir -p /temp/dev
COPY package.json bun.lock /temp/dev/
RUN cd /temp/dev && bun install --frozen-lockfile

# Stage 3: Install production dependencies (exclude devDependencies)
RUN mkdir -p /temp/prod
COPY package.json bun.lock /temp/prod/
RUN cd /temp/prod && bun install --frozen-lockfile --production

# Stage 4: Copy source code, run tests, and build the application
FROM base AS prerelease
COPY --from=install /temp/dev/node_modules node_modules
COPY . .
ENV NODE_ENV=production
RUN bun test
RUN bun run prepare
RUN bun run build

# Stage 5: Create the final release image
FROM base AS release
COPY --from=install /temp/prod/node_modules node_modules

# TODO: Shouldn't need to copy the entire source code, but copying build only doesn't work...?
COPY --from=prerelease /usr/src/app .

WORKDIR /usr/src/app/build

USER bun
EXPOSE 5173/tcp

ENTRYPOINT [ "sh", "-c", "HOST=0.0.0.0 PORT=5173 bun run ./index.js" ]
