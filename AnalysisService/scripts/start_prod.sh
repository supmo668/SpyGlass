#!/bin/bash

# Set the environment to production
export ENVIRONMENT=production

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Activate virtual environment if it exists
# if [ -d "$PROJECT_ROOT/venv" ]; then
#     source "$PROJECT_ROOT/venv/bin/activate"
# fi

# # Install requirements if needed
# if [ "$1" == "--install" ]; then
#     echo "Installing requirements..."
#     pip install -r "$PROJECT_ROOT/requirements.txt"
# fi

# Number of workers based on CPU cores (2 workers per core + 1)
# WORKERS=$(($(nproc) * 2 + 1))
WORKERS=4
# Start the FastAPI server in production mode
echo "Starting production server with $WORKERS workers..."
uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers $WORKERS \
    --log-level info \
    --no-access-log \
    --proxy-headers \
    --forwarded-allow-ips='*' \
    --app-dir "$PROJECT_ROOT"
