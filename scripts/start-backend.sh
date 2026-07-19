#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PROJECT_DIR}/.venv/bin/python"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "Python environment not found at ${PROJECT_DIR}/.venv" >&2
  echo "Create it with: python3 -m venv .venv" >&2
  exit 1
fi

cd "${PROJECT_DIR}"

if "${PYTHON_BIN}" -c "import pip" >/dev/null 2>&1; then
  PIP_CMD=("${PYTHON_BIN}" -m pip)
elif command -v python3 >/dev/null 2>&1; then
  # Some macOS Python environments retain pip's metadata but not its package.
  PIP_CMD=(python3 -m pip --python "${PYTHON_BIN}")
else
  echo "Bootstrapping pip in the project environment..."
  "${PYTHON_BIN}" -m ensurepip --upgrade >/dev/null
  PIP_CMD=("${PYTHON_BIN}" -m pip)
fi

if ! "${PYTHON_BIN}" -c "import fastapi, uvicorn" >/dev/null 2>&1; then
  echo "Installing backend dependencies..."
  "${PIP_CMD[@]}" install -r requirements.txt
fi

echo "Orqestra backend: http://${ORQ_API_HOST:-127.0.0.1}:${ORQ_API_PORT:-8000}"
UVICORN_ARGS=(
  studio.api:app
  --host "${ORQ_API_HOST:-127.0.0.1}"
  --port "${ORQ_API_PORT:-8000}"
)
if [[ "${ORQ_API_RELOAD:-false}" == "true" ]]; then
  UVICORN_ARGS+=(--reload)
fi
exec "${PYTHON_BIN}" -m uvicorn "${UVICORN_ARGS[@]}"
