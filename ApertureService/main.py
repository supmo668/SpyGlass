import os
import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
from typing import List, Optional, Dict
import json
import clip
import torch
from dotenv import load_dotenv

from tools import ApertureTools

load_dotenv()

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

app = FastAPI(
    title=config["api"]["title"],
    description=config["api"]["description"],
    version=config["api"]["version"]
)

# Initialize ApertureDB tools
aperture_tools = ApertureTools()

class Query(BaseModel):
    user_input: str
    focus_area: str = "general business opportunities"

class AnalysisStep(BaseModel):
    name: str
    result: str
    raw_response: dict

class Response(BaseModel):
    steps: List[AnalysisStep]
    final_analysis: str

class AnalysisState:
    def __init__(self):
        self.previous_results = []
        self.current_step = 0

def search_similar_companies(description: str, limit: int = 5) -> List[Dict]:
    """Search for similar companies in ApertureDB based on description."""
    try:
        # Use CLIP embeddings for semantic search
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model, preprocess = clip.load("ViT-B/16", device=device)
        
        # Generate embeddings for the search description
        search_tokens = clip.tokenize([description]).to(device)
        search_embeddings = model.encode_text(search_tokens)
        
        query = [{
            "FindDescriptor": {
                "set": "ViT-B/16",
                "k_neighbors": limit,
                "distances": True,
                "vector": search_embeddings[0].tolist(),
                "with_class": "Company",
                "results": {
                    "all_properties": True
                }
            }
        }]
        
        result, response, _ = aperture_tools.execute_query(query, [])
        if result == 0 and response:
            return response[0].get("results", [])
        return []
    except Exception as e:
        print(f"Error in search_similar_companies: {str(e)}")
        return []

def search_market_data(keywords: str, limit: int = 5) -> List[Dict]:
    """Search for market data and trends in ApertureDB based on keywords."""
    try:
        query = [{
            "FindEntity": {
                "with_class": "MarketData",
                "constraints": {
                    "keywords": ["contains", keywords]
                },
                "results": {
                    "limit": limit,
                    "all_properties": True
                }
            }
        }]
        
        result, response, _ = aperture_tools.execute_query(query, [])
        if result == 0 and response:
            return response[0].get("results", [])
        return []
    except Exception as e:
        print(f"Error in search_market_data: {str(e)}")
        return []

async def execute_analysis_step(client, messages, step_config):
    try:
        # Add tool definitions for the step
        tools = []
        if "search_market_data" in step_config["instruction"]:
            tools.append(config["aperturedb"]["tools"][1])  # Add market data search tool
        if "search_similar_companies" in step_config["instruction"]:
            tools.append(config["aperturedb"]["tools"][0])  # Add company search tool

        response = client.chat.completions.create(
            model=config["model"]["name"],
            messages=messages,
            temperature=config["model"]["temperature"],
            max_tokens=config["model"]["max_tokens"],
            tools=tools if tools else None,
            tool_choice="auto"
        )

        # Handle tool calls if any
        if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
            tool_calls = response.choices[0].message.tool_calls
            for tool_call in tool_calls:
                tool_response = await aperture_tools.handle_tool_call(tool_call)
                if tool_response:
                    messages.append(tool_response)
            
            # Get the final response after tool calls
            response = client.chat.completions.create(
                model=config["model"]["name"],
                messages=messages,
                temperature=config["model"]["temperature"],
                max_tokens=config["model"]["max_tokens"]
            )

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in step {step_config['name']}: {str(e)}")

# Initialize OpenAI client with Together AI base URL
client = openai.OpenAI(
    base_url=config["model"]["base_url"],
    api_key=os.environ['TOGETHER_API_KEY'],
)

@app.post("/analyze", response_model=Response)
async def analyze_business_opportunity(query: Query):
    try:
        # Initialize analysis state
        state = AnalysisState()
        analysis_steps = []

        # Base messages with system prompt
        messages = [
            {
                "role": "system",
                "content": config["prompts"]["system"]
            },
            {
                "role": "user",
                "content": config["prompts"]["user_template"].format(
                    user_input=query.user_input,
                    focus_area=query.focus_area
                )
            }
        ]

        # Execute each analysis step
        for step in config["prompts"]["steps"]:
            # Add step instruction to messages
            messages.append({
                "role": "user",
                "content": step["instruction"]
            })

            # Execute step
            response = await execute_analysis_step(client, messages, step)
            
            # Store step result
            step_result = response.choices[0].message.content
            messages.append({
                "role": "assistant",
                "content": step_result
            })
            
            analysis_steps.append(AnalysisStep(
                name=step["name"],
                result=step_result,
                raw_response=response.model_dump()
            ))

            # Add context from previous step
            messages.append({
                "role": "system",
                "content": f"Previous step ({step['name']}) analysis complete. Please proceed with the next step based on these findings."
            })

        return Response(
            steps=analysis_steps,
            final_analysis=analysis_steps[-1].result if analysis_steps else ""
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config["api"]["host"],
        port=config["api"]["port"]
    )
