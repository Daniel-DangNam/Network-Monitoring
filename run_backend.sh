#!/bin/bash
set -e
cd "$(dirname "$0")/backend_api"

# Tự động kích hoạt virtual environment nếu có
if [ -d "../venv" ]; then
    source ../venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "=================================================="
echo " [STARTING] FastAPI Backend Server on Ubuntu      "
echo "=================================================="
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
