#!/usr/bin/env bash
# One-command local start (no Docker needed).
# Usage:  bash start.sh
set -e

echo "=== Regulatory Document Manager ==="

# check Python
python3 --version &>/dev/null || { echo "Python 3 required"; exit 1; }

# install deps
echo "Installing dependencies…"
pip install -q -r requirements.txt

# start backend in background
echo "Starting FastAPI backend on :8000…"
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# wait for it
sleep 3
echo "Seeding sample documents…"
python scripts/seed_documents.py || true

# start frontend
echo "Starting Streamlit frontend on :8501…"
echo ""
echo "  ➜  Open http://localhost:8501 in your browser"
echo ""
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0 &
FRONTEND_PID=$!

# handle Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'; exit 0" INT TERM

wait
