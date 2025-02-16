#!/bin/bash

# Create test-result directory if it doesn't exist
mkdir -p test-result

# Get current timestamp
timestamp=$(date +%Y%m%d_%H%M%S)

# Test the analyze endpoint
echo -e "Testing analyze endpoint...\n"
curl -X POST https://simple-lobster-morally.ngrok-free.app/analyze \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Make San Francisco carbon neutral",
    "focus_area": "business_opportunities",
    "k": 5
  }' | tee "test-result/analysis_${timestamp}.json"

echo -e "\nResult saved to test-result/analysis_${timestamp}.json\n"