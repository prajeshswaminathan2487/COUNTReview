#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "== COUNT/REACH Generator setup =="

if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

source venv/bin/activate

echo "Installing dependencies..."
pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
  echo ""
  echo "No .env file found."
  echo "Copy .env.example to .env and fill in your Azure OpenAI details:"
  echo "    cp .env.example .env"
  echo ""
  exit 1
fi

export $(grep -v '^#' .env | xargs)

if [ -z "$AZURE_OPENAI_API_KEY" ] || [ "$AZURE_OPENAI_API_KEY" = "paste-your-key-here" ]; then
  echo ""
  echo "AZURE_OPENAI_API_KEY is not set in .env — edit .env with your real values."
  echo ""
  exit 1
fi

echo ""
echo "Starting the app..."
python app.py
