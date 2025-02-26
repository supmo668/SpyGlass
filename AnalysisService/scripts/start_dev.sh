#!/bin/bash

# Set the environment to development
export ENVIRONMENT=development

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Activate virtual environment if it exists
if [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# Install requirements if needed
if [ "$1" == "--install" ]; then
    echo "Installing requirements..."
    pip install -r "$PROJECT_ROOT/requirements.txt"
fi

# Start the FastAPI server with auto-reload
echo "Starting development server..."
uvicorn main:app --reload --host 0.0.0.0 --port 8080 --workers 1 \
    --log-level debug \
    --reload-dir "$PROJECT_ROOT" \
    --app-dir "$PROJECT_ROOT"
