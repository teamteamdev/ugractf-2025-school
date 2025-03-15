# syntax=docker.io/docker/dockerfile:1

FROM golang:alpine AS proxy-builder

WORKDIR /app
COPY proxy.go ./
RUN CGO_ENABLED=0 GOOS=linux go build -a -ldflags="-s -w" -o proxy proxy.go

FROM node:22-alpine AS base

FROM base AS deps

RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci; \
    # our build engine can't build C++, so we build C
    sed -i 's/c++/c=1/g' node_modules/cuid/index.js

# Speaking seriously, cuid is patched to emulate serverless deployments, where
# container may be launched for each single invocation (e.g. user request).

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules/ ./node_modules/
COPY .eslintrc.json next-env.d.ts next.config.js package-lock.json package.json tsconfig.json ./
COPY app/ ./app/
COPY public/ ./public/

ENV NEXT_TELEMETRY_DISABLED=1
ENV BASE_PATH=/_REPLACE_ME_

RUN npm run build

FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV BASE_PATH=/_REPLACE_ME_

COPY --from=builder /app/public/ ./public/
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static/
COPY --from=proxy-builder /app/proxy ./
COPY run.sh ./

EXPOSE 3001
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

ENV UPLOAD_DIR=/state/uploads
ENV DATABASE_PATH=/state/dbs

CMD ["./run.sh"]
