import os
import yaml
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import traceback
import weave
import tempfile
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# Initialize Weave
weave.init("SpyGlass-API")

from agent import run_analysis
from tools import ApertureTools
from langchain_core.documents import Document

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=config["api"]["title"],
    description=config["api"]["description"],
    version=config["api"]["version"]
)

# Initialize ApertureDB tools
aperture_tools = ApertureTools()

class TrendOp(BaseModel):
    Trend: str
    Year_2025: float
    Year_2026: float
    Year_2027: float
    Year_2028: float
    Year_2029: float
    Year_2030: float
    Startup_Opportunity: str
    Growth_rate_WoW: float
    YC_chances: float
    Related_trends: str

class IntermediateStep(BaseModel):
    content: str
    timestamp: str

class IntermediateResults(BaseModel):
    trend_analysis: IntermediateStep
    opportunity_analysis: IntermediateStep
    competitor_analysis: IntermediateStep
    final_analysis: IntermediateStep

class AnalysisInput(BaseModel):
    generate_novel_ideas: bool = True
    user_query: str
    k: int = Field(default=10, ge=1, le=50, description="Number of trends to generate")

@weave.op()
async def analyze_business_opportunity(query: AnalysisInput) -> List[TrendOp]:
    """
    Analyze a business opportunity and generate k trend operations.
    """
    try:
        logger.info(f"Received analysis request: {query.user_query}")
        
        # Run the multi-step analysis
        result = await run_analysis(
            user_input=query.user_query,
            focus_area="business opportunities",
            generate_novel=query.generate_novel_ideas,
            k=query.k
        )
        
        logger.info("Analysis completed successfully")
        
        # Process the analysis into trend operations
        trend_ops = []
        for trend in result.get("trends", []):
            trend_op = TrendOp(
                Trend=trend["name"],
                Startup_Opportunity=trend["Startup_Opportunity"],
                Growth_rate_WoW=trend.get("growth_rate", 0.0),
                YC_chances=trend.get("yc_chances", 0.0),
                Year_2025=trend.get("year_2025", 0.0),
                Year_2026=trend.get("year_2026", 0.0),
                Year_2027=trend.get("year_2027", 0.0),
                Year_2028=trend.get("year_2028", 0.0),
                Year_2029=trend.get("year_2029", 0.0),
                Year_2030=trend.get("year_2030", 0.0),
                Related_trends=", ".join(trend.get("related_trends", []))
            )
            trend_ops.append(trend_op)
        
        # Create a temporary file to store the JSON data
        if query.generate_novel_ideas and trend_ops:
            try:
                # Create intermediate results
                intermediate = IntermediateResults(
                    trend_analysis=IntermediateStep(
                        content=result["trend_analysis"],
                        timestamp=datetime.now().isoformat()
                    ),
                    opportunity_analysis=IntermediateStep(
                        content=result["opportunity_analysis"],
                        timestamp=datetime.now().isoformat()
                    ),
                    competitor_analysis=IntermediateStep(
                        content=result["competitor_analysis"],
                        timestamp=datetime.now().isoformat()
                    ),
                    final_analysis=IntermediateStep(
                        content=result["final_analysis"],
                        timestamp=datetime.now().isoformat()
                    )
                )

                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
                    # Convert trend_ops to JSON with intermediate results
                    json_data = {
                        "query": query.user_query,
                        "timestamp": datetime.now().isoformat(),
                        "trends": [trend.dict() for trend in trend_ops],
                        "intermediate_results": intermediate.dict()
                    }
                    import json
                    json.dump(json_data, tmp, indent=2)
                    tmp_path = tmp.name

                # Read the temporary file and index it
                with open(tmp_path, 'r') as f:
                    content = f.read()
                    document = Document(
                        page_content=content,
                        metadata={
                            "type": "trend_analysis",
                            "query": query.user_query,
                            "timestamp": datetime.now().isoformat(),
                            "num_trends": len(trend_ops),
                            "has_intermediate_results": True
                        }
                    )
                    await aperture_tools.add_document(document)
                    logger.info(f"Successfully indexed {len(trend_ops)} trends with intermediate results")

                # Clean up the temporary file
                Path(tmp_path).unlink()
            except Exception as e:
                logger.error(f"Error indexing trends: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
        
        return trend_ops[:query.k]  # Ensure we only return k trends

    except Exception as e:
        logger.error(f"Error processing analysis request: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze", response_model=List[TrendOp])
async def analyze(query: AnalysisInput) -> List[TrendOp]:
    """
    API endpoint to analyze business opportunities and generate startup ideas.
    Returns a list of k trend operations.
    """
    return await analyze_business_opportunity(query)

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
