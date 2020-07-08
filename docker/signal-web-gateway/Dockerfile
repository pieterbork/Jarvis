FROM golang:alpine as builder

RUN apk --no-cache add git mercurial

RUN go get github.com/sirupsen/logrus \
    && go get github.com/pieterbork/textsecure \
    && go get github.com/go-redis/redis \
    && cd /go/src/github.com/pieterbork/textsecure/cmd/textsecure \
    && go build \
    && mkdir /output \
    && mv /go/src/github.com/pieterbork/textsecure/cmd/textsecure/textsecure /output

FROM alpine:latest

WORKDIR /signal

COPY --from=builder /output /signal

COPY entrypoint.sh /

RUN apk --no-cache add \
      ca-certificates \
      sudo \
    && addgroup -g 2003 signal \
    && adduser -u 2003 -G signal -h /signal -s /bin/sh -D signal \
    && echo "%signal ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/signal \
    && chmod 400 /etc/sudoers.d/signal \
    && apk --no-cache add \
      bash \
      tini

USER signal

ENTRYPOINT ["/sbin/tini", "--", "/entrypoint.sh"]

EXPOSE 5000

