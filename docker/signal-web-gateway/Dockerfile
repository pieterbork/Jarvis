FROM golang:alpine as builder

RUN apk --no-cache add git mercurial

RUN go get github.com/sirupsen/logrus \
    && go get github.com/pieterbork/textsecure/ \
    && go get github.com/go-redis/redis \
    && cd src/github.com/pieterbork/textsecure/cmd/textsecure \
    && go build \
    && mv /go/src/github.com/pieterbork/textsecure/cmd/textsecure /output \
    && rm -f /output/main.go

FROM alpine:latest

WORKDIR /signal

COPY --from=builder /output /signal

COPY entrypoint.sh /

RUN apk --no-cache add \
      ca-certificates \
      sudo \
    && addgroup signal \
    && adduser -G signal -h /signal -s /bin/sh -D signal \
    && echo "%signal ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/signal \
    && chmod 400 /etc/sudoers.d/signal \
    && apk --no-cache add \
      bash \
      tini

USER signal

ENTRYPOINT ["/sbin/tini", "--", "/entrypoint.sh"]

EXPOSE 5000

