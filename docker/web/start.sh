#!/bin/sh
set -e

echo "Waiting for API at http://api:8000/health ..."
for i in $(seq 1 60); do
  if wget -qO- http://api:8000/health >/dev/null 2>&1; then
    echo "API is up."
    exec nginx -g 'daemon off;'
  fi
  sleep 1
done

echo "API not reachable after 60s. Starting nginx anyway..."
exec nginx -g 'daemon off;'
