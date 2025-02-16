#!/bin/bash

# Create test-result directory if it doesn't exist
mkdir -p test-result

# Get current timestamp
timestamp=$(date +%Y%m%d_%H%M%S)

# Test the analyze endpoint
echo "Testing analyze endpoint..."
curl -X POST http://localhost:8000/analyze \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "Make San Francisco carbon neutral",
    "focus_area": "business_opportunities",
    "k": 10
  }' | tee "test-result/analysis_${timestamp}.json"

# # Test the index endpoint with a sample document
# echo -e "\n\nTesting index endpoint..."
# echo '{
#   "title": "Sample Market Research",
#   "content": "AI in healthcare is growing rapidly...",
#   "date": "2025-02-16"
# }' > /tmp/sample.json

# curl -X POST http://localhost:8000/index \
#   -H "Content-Type: multipart/form-data" \
#   -F "file=@/tmp/sample.json"

# rm /tmp/sample.json

# # Test the search endpoint
# echo -e "\n\nTesting search endpoint..."
# curl -X GET "http://localhost:8000/search?query=AI%20healthcare&limit=2"

echo -e "\nAll tests completed!"
