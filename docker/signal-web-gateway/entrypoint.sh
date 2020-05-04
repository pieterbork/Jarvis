#!/bin/bash

start() {
  ./textsecure -gateway -bind 0.0.0.0:5000 -redismode -redisbind redis:6379
}

stop() {
  echo "[ERROR] It looks like your Signal identity has not been setup properly, please follow instructions on how to register an account"
}

entrypoint() {
  ls -al /signal/.storage/identity
  if [ -f /signal/.storage/identity/identity_key ]; then
    start
  else
    stop
  fi
}

sudo chown -R signal:signal .storage .config

if [ ! -z "$1" ]; then
  case "$1" in
    "register")
      ./textsecure
    ;;
    "config")
      cat .config/config.yml
    ;;
    "*")
      entrypoint
    ;;
  esac
else
  entrypoint
fi

