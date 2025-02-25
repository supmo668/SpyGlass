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
import hashlib
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
log_file = os.path.join(os.path.dirname(__file__), "app.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
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
    # Startup: Initialize in-memory cache with a larger size
    backend = InMemoryBackend()
    FastAPICache.init(backend, prefix="spyglass-cache:", coder=JsonCoder)
    logger.info("Cache initialized")
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

def get_cache_key(query: AnalysisInput) -> str:
    """Generate a deterministic cache key from the query."""
    # Create a string with all relevant query parameters
    key_str = f"{query.user_input}:{query.k}:{query.generate_novel_ideas}"
    # Create a hash to ensure the key is a valid cache key
    return f"analyze:{hashlib.md5(key_str.encode()).hexdigest()}"

async def cached_analysis(query: AnalysisInput) -> AnalysisOutput:
    """Cached wrapper for the analysis computation."""
    try:
        logger.info(f"Cache miss - Starting heavy computation for: {query.user_input}")
        start_time = datetime.now()
        
        # Run the analysis - it creates its own IntermediateResults
        results = await run_analysis(query)
        
        # Update execution time if needed
        if not results.execution_time:
            end_time = datetime.now()
            results.execution_time = (end_time - start_time).total_seconds()
        
        logger.info(f"Analysis computation completed in {results.execution_time:.2f} seconds")
        
        # Return the results
        return AnalysisOutput(
            status="success",
            data={
                "trend_analysis": results.trend_analysis.model_dump() if results.trend_analysis else None,
                "opportunity_analysis": results.opportunity_analysis.model_dump() if results.opportunity_analysis else None,
                "competitor_analysis": results.competitor_analysis.model_dump() if results.competitor_analysis else None,
                "final_result": results.final_result.model_dump() if results.final_result else None,
                "execution_time": results.execution_time,
                "refinement_steps": [step.model_dump() for step in results.refinement_steps] if results.refinement_steps else []
            }
        )
    except Exception as e:
        logger.error(f"Error in cached analysis: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return AnalysisOutput(
            status="error",
            data={},
            error=str(e)
        )

@weave.op()
async def analyze_business_opportunity(query: AnalysisInput) -> AnalysisOutput:
    """Analyze a business opportunity and return trend analysis with intermediate steps."""
    # Map user_query to user_input if needed
    if hasattr(query, 'user_query') and not hasattr(query, 'user_input'):
        query.user_input = query.user_query
        
    # Get cache key
    cache_key = get_cache_key(query)
    logger.info(f"Checking cache for key: {cache_key}")
    
    # Try to get from cache first
    try:
        backend = FastAPICache.get_backend()
        cached_result = await backend.get(cache_key)
        if cached_result is not None:
            logger.info(f"Cache hit for: {query.user_input}")
            return JsonCoder.decode(cached_result)
    except Exception as e:
        logger.warning(f"Cache check failed: {str(e)}")
    
    # If not in cache, compute and store
    result = await cached_analysis(query)
    try:
        backend = FastAPICache.get_backend()
        await backend.set(cache_key, JsonCoder.encode(result), expire=30 * 24 * 60 * 60)  # 30 days
    except Exception as e:
        logger.warning(f"Failed to store in cache: {str(e)}")
    
    return result

@app.post("/analyze", response_model=AnalysisOutput)
async def analyze(query: AnalysisInput) -> AnalysisOutput:
    """Analyze a business opportunity and return trend analysis with all intermediate steps."""
    try:
        return await analyze_business_opportunity(query)
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
