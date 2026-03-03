#!/usr/bin/env bash
set -euo pipefail

echo "[CHECK] Ensuring no venv/env files are tracked..."
if git ls-files | grep -E '^(\.venv|venv|env)/' >/dev/null; then
  echo "ERROR: Virtual environment files are tracked in git. Remove them!"
  exit 1
fi

echo "[CHECK] Ensuring no .env is tracked..."
if git ls-files | grep -E '^\.env$' >/dev/null; then
  echo "ERROR: .env is tracked in git. Remove it!"
  exit 1
fi

echo "[CHECK] Ensuring no voice models are tracked..."
if git ls-files | grep -E '\.onnx(\.json)?$' >/dev/null; then
  echo "ERROR: Voice models are tracked in git. Remove them!"
  exit 1
fi

echo "[CHECK] Ensuring no site-packages / binaries are tracked..."
if git ls-files | grep -E 'site-packages|\.so$|\.dylib$' >/dev/null; then
  echo "ERROR: Binary artifacts/site-packages tracked in git. Remove them!"
  exit 1
fi

echo "OK: Repo looks clean."