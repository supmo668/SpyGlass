# SpyGlass Analysis Service

The Analysis Service is a FastAPI-based microservice that provides business opportunity analysis through a series of sequential steps including trend analysis, opportunity analysis, and competitor analysis.

## Features

- Sequential analysis workflow
- Intermediate results tracking
- Quality-based refinement
- Structured output using Pydantic models
- Comprehensive error handling

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SpyGlass.git
cd SpyGlass/AnalysisService
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Usage

### Starting the Service

```bash
uvicorn main:app --reload
```

The service will be available at `http://localhost:8000`

### API Endpoints

#### POST /analyze

Analyzes a business opportunity based on user input.

**Request Body:**

```json
{
    "user_input": "Make San Francisco carbon neutral",
    "generate_novel_ideas": true,
    "k": 5
}
```

**Parameters:**
- `user_input`: (string, required) The business opportunity or idea to analyze
- `generate_novel_ideas`: (boolean) Whether to generate novel ideas
- `k`: (integer) Number of trends/opportunities to generate

**Response:**

```json
{
    "status": "success",
    "data": {
        "trend_analysis": {
            "step_name": "trend_analysis",
            "output": "...",
            "timestamp": "2025-02-20T02:15:16Z",
            "is_refined": false,
            "refinement_count": 0
        },
        "opportunity_analysis": {
            "step_name": "opportunity_analysis",
            "output": "...",
            "timestamp": "2025-02-20T02:15:17Z",
            "is_refined": false,
            "refinement_count": 0
        },
        "competitor_analysis": {
            "step_name": "competitor_analysis",
            "output": "...",
            "timestamp": "2025-02-20T02:15:18Z",
            "is_refined": false,
            "refinement_count": 0
        },
        "final_result": {
            "trends": [],
            "opportunities": [],
            "competitors": []
        },
        "execution_time": 5.23,
        "refinement_steps": []
    },
    "error": null
}
```

### Example Usage

Here's a script to test the analyze endpoint:

```bash
#!/bin/bash

# API endpoint
API_URL="http://localhost:8000"

# Test with default parameters
curl -X POST "${API_URL}/analyze" \
    -H "Content-Type: application/json" \
    -d '{
        "user_input": "Make San Francisco carbon neutral",
        "generate_novel_ideas": true,
        "k": 5
    }'

# Test with different parameters
curl -X POST "${API_URL}/analyze" \
    -H "Content-Type: application/json" \
    -d '{
        "user_input": "a startup in the AI healthcare space to curate and summarize doctor notes into patient insights",
        "generate_novel_ideas": false,
        "k": 3
    }'
```

## Development

### Project Structure

```
AnalysisService/
├── main.py           # FastAPI application and endpoints
├── agent.py          # Analysis workflow implementation
├── models.py         # Pydantic data models
├── config.yaml       # Configuration settings
├── scripts/          # Utility scripts
└── tests/           # Test files
```

### Running Tests

```bash
pytest
```

### Configuration

The service can be configured through:
1. Environment variables in `.env`
2. Configuration settings in `config.yaml`

## Error Handling

The service provides structured error responses:

```json
{
    "status": "error",
    "data": {},
    "error": "Error message details"
}
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
