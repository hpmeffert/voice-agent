#!/bin/sh
set -e

echo "[web-agent] waiting for api: http://api:8000/health"
for i in $(seq 1 90); do
  if wget -qO- http://api:8000/health >/dev/null 2>&1; then
    echo "[web-agent] api is ready"
    break
  fi
  sleep 1
done

echo "[web-agent] waiting for piper: http://piper:5002/health"
for i in $(seq 1 90); do
  if wget -qO- http://piper:5002/health >/dev/null 2>&1; then
    echo "[web-agent] piper is ready"
    break
  fi
  sleep 1
done

echo "[web-agent] starting nginx"
exec nginx -g 'daemon off;'
