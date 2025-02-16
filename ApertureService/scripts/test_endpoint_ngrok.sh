#!/bin/bash

# Test the analyze endpoint
echo "Testing analyze endpoint..."
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "generate_novel_ideas": true,
    "user_query": "Make San Francisco carbon neutral",
    "k": 3
  }'



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
