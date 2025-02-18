#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# API endpoint
API_URL="http://localhost:8000"

curl -X POST "${API_URL}/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Make San Francisco carbon neutral",
    "k": 5
  }' | tee "test-result/analysis_${timestamp}.json"

echo -e "\nResult saved to test-result/analysis_${timestamp}.json\n"