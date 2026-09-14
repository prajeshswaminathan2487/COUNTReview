#!/bin/bash
set -e
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
  echo "No .env file found. Run: cp .env.example .env   (then edit it)"
  exit 1
fi

export $(grep -v '^#' .env | xargs)

if [ -z "$GEMINI_API_KEY" ] || [ "$GEMINI_API_KEY" = "paste-your-key-here" ]; then
  echo "GEMINI_API_KEY is not set in .env — edit .env with your real key."
  exit 1
fi

python app.py
