#!/bin/sh
set -e

echo "[web] waiting for api: http://api:8000/health"
for i in $(seq 1 90); do
  if wget -qO- http://api:8000/health >/dev/null 2>&1; then
    echo "[web] api is ready"
    break
  fi
  sleep 1
done

echo "[web] waiting for piper: http://piper:5002/health"
for i in $(seq 1 90); do
  if wget -qO- http://piper:5002/health >/dev/null 2>&1; then
    echo "[web] piper is ready"
    break
  fi
  sleep 1
done

echo "[web] starting nginx"
exec nginx -g 'daemon off;'
