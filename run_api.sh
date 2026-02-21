#!/bin/bash
cd "$(dirname "$0")"

# Load environment variables if .env exists
if [ -f .env ]; then
  source .env
fi

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Run the FastAPI server using uvicorn
echo "Starting AMS-IO-Agent backend on port 8000..."
python3 -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
