from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import yaml
import weave
import traceback
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from fastapi_cache.coder import JsonCoder
from contextlib import asynccontextmanager

from models import (
    AnalysisInput,
    StartupAnalysisResponse,
    IntermediateResults,
    AnalysisOutput,
    FileUploadResponse
)
from agent import run_analysis

# Load environment variables
load_dotenv()

# Initialize Weave
weave.init("SpyGlass-API")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load configuration
config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# Create FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize in-memory cache
    FastAPICache.init(InMemoryBackend(), prefix="spyglass-cache:", coder=JsonCoder)
    yield
    # Shutdown: Nothing to clean up for in-memory cache

app = FastAPI(
    title="SpyGlass API",
    description="API for business opportunity analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
origins = [
    "http://localhost:3000",  # Next.js development server
    "http://localhost:8000",  # FastAPI development server
    "https://spyglass-ui.vercel.app",  # Production UI
    "https://*.ngrok-free.app",  # ngrok tunnels
    "*"  # Allow all origins temporarily for debugging
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,  # Cache preflight requests for 24 hours
)

@weave.op()
async def analyze_business_opportunity(query: AnalysisInput) -> AnalysisOutput:
    """Analyze a business opportunity and return trend analysis with intermediate steps."""
    try:
        # Map user_query to user_input if needed
        if hasattr(query, 'user_query') and not hasattr(query, 'user_input'):
            query.user_input = query.user_query
            
        # Log the request
        logger.info(f"Received analysis request: {query.user_input}")
        
        # Run analysis and get results including intermediate steps
        results = await run_analysis(query)
        
        # Return structured response
        return AnalysisOutput(
            status="success",
            data={
                "trend_analysis": results.trend_analysis.model_dump() if results.trend_analysis else None,
                "opportunity_analysis": results.opportunity_analysis.model_dump() if results.opportunity_analysis else None,
                "competitor_analysis": results.competitor_analysis.model_dump() if results.competitor_analysis else None,
                "final_result": results.final_result.model_dump() if results.final_result else None,
                "execution_time": results.execution_time,
                # Change 'steps' to 'refinement_steps'
                "refinement_steps": [step.model_dump() for step in results.refinement_steps] if results.refinement_steps else []
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing analysis request: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return AnalysisOutput(
            status="error",
            data={},
            error=str(e)
        )

@app.post("/analyze", response_model=AnalysisOutput)
@cache(expire=30 * 24 * 60 * 60, key_builder=lambda query: f"analyze:{query.user_input}:{query.k}")  # Cache for 30 days
async def analyze(query: AnalysisInput) -> AnalysisOutput:
    """Analyze a business opportunity and return trend analysis with all intermediate steps."""
    try:
        logger.info(f"Processing analysis request for: {query.user_input}")
        result = await analyze_business_opportunity(query)
        logger.info(f"Analysis completed for: {query.user_input}")
        return result
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}")
        return AnalysisOutput(
            status="error",
            data={},
            error=str(e)
        )

@app.post("/index", response_model=FileUploadResponse)
async def index(file: UploadFile = File(...)) -> FileUploadResponse:
    """Index a file for analysis."""
    try:
        logger.info(f"Received document indexing request: {file.filename}")
        
        # Create a temporary file to store the uploaded content
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Read the temporary file and index it
        with open(tmp_path, 'r') as f:
            content = f.read()
            document = Document(
                page_content=content,
                metadata={
                    "filename": file.filename,
                    "timestamp": datetime.now().isoformat()
                }
            )
            await aperture_tools.add_document(document)
        
        # Clean up the temporary file
        Path(tmp_path).unlink()
        
        logger.info(f"Successfully indexed document: {file.filename}")
        return FileUploadResponse(
            status="success",
            file_id="temp_id"
        )
    except Exception as e:
        logger.error(f"Error in file upload: {str(e)}")
        return FileUploadResponse(
            status="error",
            error=str(e)
        )

@app.get("/search")
async def search(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    API endpoint to search for documents.
    """
    try:
        logger.info(f"Received search request: query='{query}', limit={limit}")
        
        # Search documents
        results = await aperture_tools.search_similar_documents(query, k=limit)
        
        logger.info(f"Found {len(results)} matching documents")
        return results
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config["api"]["host"],
        port=config["api"]["port"]
    )
