#!/bin/bash

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default values
HOST="localhost"
PORT="8000"
FOCUS_AREA="artificial intelligence"
USER_INPUT="Analyze the potential of AI in healthcare, focusing on diagnostic tools and patient care optimization"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --focus)
            FOCUS_AREA="$2"
            shift 2
            ;;
        --input)
            USER_INPUT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Construct the JSON payload
JSON_PAYLOAD=$(cat << EOF
{
    "user_input": "$USER_INPUT",
    "focus_area": "$FOCUS_AREA"
}
EOF
)

# Make the curl request
echo "Testing endpoint with payload:"
echo "$JSON_PAYLOAD" | jq '.'
echo -e "\nSending request to http://$HOST:$PORT/analyze..."

curl -X POST "http://$HOST:$PORT/analyze" \
     -H "Content-Type: application/json" \
     -d "$JSON_PAYLOAD" | jq '.'
