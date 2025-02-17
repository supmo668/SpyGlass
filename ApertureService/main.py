import os
import yaml
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import logging
import traceback
import weave
import tempfile
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from fastapi.middleware.cors import CORSMiddleware
from langchain.output_parsers import PydanticOutputParser
from agent import (
    run_analysis,
    AnalysisInput,
    StartupAnalysisResponse
)
from models import (
    AnalysisInput,
    StartupAnalysisResponse
)


# Initialize Weave
weave.init("SpyGlass-API")

from tools import ApertureTools
from langchain_core.documents import Document

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=config["api"]["title"],
    description=config["api"]["description"],
    version=config["api"]["version"]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods including OPTIONS preflight
    allow_headers=[
        "*"
    ],
    expose_headers=["*"],  # Expose all headers to the browser
    max_age=86400,  # Cache preflight requests for 24 hours
)

# Initialize ApertureDB tools
aperture_tools = ApertureTools()

@weave.op()
async def analyze_business_opportunity(query: AnalysisInput) -> str:
    """Analyze a business opportunity and return trend analysis."""
    try:
        # Extract parameters
        user_input = query.user_input
        focus_area = "business opportunities"
        k = query.k
        
        # Log the request
        logger.info(f"Received analysis request: {user_input}")
        
        # Run analysis and return result
        result = await run_analysis(
            user_input=user_input,
            focus_area=focus_area,
            generate_novel=query.generate_novel_ideas,
            k=k
        )
        return result
        
    except Exception as e:
        logger.error(f"Error processing analysis request: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze", response_model=Union[StartupAnalysisResponse, str])
async def analyze(query: AnalysisInput) -> Union[StartupAnalysisResponse, str]:
    """
    API endpoint to analyze business opportunities and generate startup ideas.
    Returns a trend analysis response or raw string if parsing fails.
    """
    try:
        json_str = await analyze_business_opportunity(query)
        
        # Use LangChain's PydanticOutputParser
        parser = PydanticOutputParser(pydantic_object=StartupAnalysisResponse)
        try:
            return parser.parse(json_str)
        except Exception as e:
            logger.warning(f"Failed to parse response as StartupAnalysisResponse: {e}")
            return json_str
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/index")
async def index(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    API endpoint to index a document.
    """
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
        return {
            "status": "success",
            "message": f"Document {file.filename} indexed successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error indexing document: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

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
