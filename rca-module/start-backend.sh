#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/backend"
if [ ! -d "venv" ]; then
  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
else
  source venv/bin/activate
fi
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo ""
  echo ">>> Created backend/.env — open it and paste your GROQ_API_KEY"
  echo ""
fi
echo "Starting FastAPI on http://localhost:8000 ..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
