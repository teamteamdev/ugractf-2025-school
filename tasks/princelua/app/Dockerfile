FROM alpine:3.21 AS builder-runner

RUN apk add --no-cache build-base lua5.4-dev
ENV C_INCLUDE_PATH=/usr/include/lua5.4

COPY ./runner /build
WORKDIR /build

RUN make run_alpine

FROM golang:alpine3.21 AS builder-app

ENV GOOS=linux
ENV CGO_ENABLED=0

WORKDIR /build
COPY go.mod /build/
RUN go mod download

COPY *.go /build/
RUN go build -o app .

FROM alpine:3.21

WORKDIR /app

COPY --from=builder-runner /build/run_alpine /app/run
COPY --from=builder-app /build/app /app/app

CMD [ "/app/app" ]
