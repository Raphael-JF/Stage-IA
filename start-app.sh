#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/server"
source venv/bin/activate
uvicorn api.main:app --host 0.0.0.0 --port 8000
