#!/bin/bash

start() {
  ./textsecure -gateway -bind 0.0.0.0:5000
}

stop() {
  echo "[ERROR] It looks like your Signal identity has not been setup properly, please follow instructions on how to register an account"
}

entrypoint() {
  if [ -f /signal/.storage/identity/identity_key ]; then
    start
  else
    stop
  fi
}

sudo chown -R 2003:2003 .storage .config

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

