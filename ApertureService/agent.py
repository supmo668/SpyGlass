from typing import Annotated, Literal, Sequence, TypedDict, List, Dict, Any, Optional, Union
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_together import ChatTogether
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from langgraph.graph import END, StateGraph, START
import logging
import traceback
import yaml
import json
import os
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(
    filename='debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
try:
    with open("config.yaml", "r") as f:
        config: Dict[str, Any] = yaml.safe_load(f)
except Exception as e:
    logger.error(f"Failed to load config.yaml: {str(e)}")
    raise

# Initialize model
try:
    model: ChatTogether = ChatTogether(
        model=config["model"]["name"],
        temperature=config["model"]["temperature"],
        max_tokens=config["model"]["max_tokens"],
        together_api_key=os.environ['TOGETHERAI_API_KEY'],
        base_url=config["model"]["base_url"],
        max_retries=2,
        timeout=120  # 2 minute timeout
    )
except Exception as e:
    logger.error(f"Failed to initialize ChatTogether model: {str(e)}")
    raise

class TrendOp(BaseModel):
    """Model for a trend operation analysis."""
    name: str = Field(description="Name of the trend")
    description: str = Field(description="Detailed description of the trend")
    Year_2025: float = Field(description="Projected adoption/impact percentage for 2025 (0.0 to 1.0)")
    Year_2026: float = Field(description="Projected adoption/impact percentage for 2026 (0.0 to 1.0)")
    Year_2027: float = Field(description="Projected adoption/impact percentage for 2027 (0.0 to 1.0)")
    Year_2028: float = Field(description="Projected adoption/impact percentage for 2028 (0.0 to 1.0)")
    Year_2029: float = Field(description="Projected adoption/impact percentage for 2029 (0.0 to 1.0)")
    Year_2030: float = Field(description="Projected adoption/impact percentage for 2030 (0.0 to 1.0)")
    Startup_Opportunity: str = Field(description="Detailed description of the startup opportunity related to this trend")
    Growth_rate_WoW: float = Field(description="Week-over-week growth rate as a decimal (0.0 to 1.0)")
    YC_chances: float = Field(description="Probability of YC investment success as a decimal (0.0 to 1.0)")
    Related_trends: str = Field(description="Comma-separated list of related trends")

class KTrendOps(BaseModel):
    """Container for multiple trend operations."""
    trends: List[TrendOp] = Field(description="List of trend operations to analyze")

class AnalysisState(TypedDict):
    """Type definition for analysis state."""
    messages: List[Any]
    focus_area: str
    user_input: str
    trend_analysis: str
    opportunity_analysis: str
    competitor_analysis: str
    final_analysis: str
    current_step: int
    trends: List[Dict[str, Any]]
    k: int
    retry_count: int

def save_analysis_result(result: Dict[str, Any], focus_area: str) -> str:
    """Save analysis result to a JSON file in the results directory."""
    # Create results directory if it doesn't exist
    results_dir: str = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id: str = uuid.uuid4().hex[:8]
    filename: str = f"{timestamp}_{focus_area.lower().replace(' ', '_')}_{run_id}.json"
    filepath: str = os.path.join(results_dir, filename)
    
    # Save result
    with open(filepath, 'w') as f:
        json.dump(result, f, indent=2)
    
    logger.info(f"Saved analysis result to {filepath}")
    return filepath

def check_analysis_quality(state: AnalysisState, retry_count: int = 0) -> Dict[str, Any]:
    """Check the quality of the analysis and request refinement if needed."""
    logger.info("---CHECK ANALYSIS QUALITY---")
    try:
        messages: List[Any] = state.get("messages", [])
        trends: List[Dict[str, Any]] = state.get("trends", [])
        
        if not trends and retry_count < 2:
            new_state = state.copy()
            new_state["retry_count"] = retry_count + 1
            new_state["next"] = "analyze_trends"
            return new_state
            
        new_state = state.copy()
        new_state["next"] = "analyze_opportunities"
        return new_state
        
    except Exception as e:
        logger.error(f"Error in quality check: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"next": "analyze_opportunities", "error": str(e)}

async def _analyze_trends(state: AnalysisState) -> str:
    """Analyze trends based on user input."""
    try:
        # Initialize model with ChatTogether using config
        chat_model = ChatTogether(
            model=config["model"]["name"],
            temperature=config["model"]["temperature"],
            max_tokens=config["model"]["max_tokens"],
            together_api_key=os.environ['TOGETHERAI_API_KEY'],
            base_url=config["model"]["base_url"],
            max_retries=2,
            timeout=120
        )
        
        # Initialize parser
        trend_parser = PydanticOutputParser(pydantic_object=KTrendOps)
        format_instructions = trend_parser.get_format_instructions()
        
        # Create prompt
        prompt = PromptTemplate(
            template=config.get("prompts", {}).get("trend_analysis", ""),
            input_variables=["format_instructions", "user_input", "k"]
        )
        
        # Create messages
        messages = [
            SystemMessage(content=config.get("prompts", {}).get("system", "")),
            HumanMessage(content=prompt.format(
                format_instructions=format_instructions,
                user_input=state.get("focus_area", "business opportunities"),
                k=state.get("k", 10)
            ))
        ]
        
        # Get response and return content directly
        response = await chat_model.ainvoke(messages)
        logger.debug(f"Trend analysis response: {response.content}")
        return response.content
        
    except Exception as e:
        logger.error(f"Error in analyze_trends: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def analyze_opportunities(state: AnalysisState) -> Dict[str, Any]:
    """Analyze opportunities based on trends."""
    logger.info("---ANALYZE OPPORTUNITIES---")
    try:
        messages: List[Any] = state.get("messages", [])
        trends: List[Dict[str, Any]] = state.get("trends", [])
        
        prompt: PromptTemplate = PromptTemplate(
            template=config.get("prompts", {}).get("opportunity_analysis", ""),
            input_variables=["trend_analysis", "user_input"]
        )
        
        new_messages: List[Any] = [
            SystemMessage(content=prompt.format(
                trend_analysis=str(trends),
                user_input=messages[0].content if messages else ""
            )),
            messages[0] if messages else HumanMessage(content="")
        ]
        
        response: Any = model.invoke(new_messages)
        logger.debug(f"Opportunity analysis response: {response.content}")
        
        new_state = state.copy()
        new_state["messages"] = [*messages, response]
        new_state["opportunity_analysis"] = response.content
        new_state["next"] = "competitors"
        
        return new_state

    except Exception as e:
        logger.error(f"Error in opportunity analysis: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"next": "competitors", "error": str(e)}

def analyze_competitors(state: AnalysisState) -> Dict[str, Any]:
    """Analyze competitors based on opportunities."""
    logger.info("---ANALYZE COMPETITORS---")
    try:
        messages: List[Any] = state.get("messages", [])
        opportunity_analysis: str = state.get("opportunity_analysis", "")
        
        prompt: PromptTemplate = PromptTemplate(
            template=config.get("prompts", {}).get("competitor_analysis", ""),
            input_variables=["opportunity_analysis", "user_input"]
        )
        
        new_messages: List[Any] = [
            SystemMessage(content=prompt.format(
                opportunity_analysis=opportunity_analysis,
                user_input=messages[0].content if messages else ""
            )),
            messages[0] if messages else HumanMessage(content="")
        ]
        
        response: Any = model.invoke(new_messages)
        logger.debug(f"Competitor analysis response: {response.content}")
        
        new_state = state.copy()
        new_state["messages"] = [*messages, response]
        new_state["competitor_analysis"] = response.content
        new_state["next"] = "generate"
        
        return new_state

    except Exception as e:
        logger.error(f"Error in competitor analysis: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"next": "generate", "error": str(e)}

def generate_final(state: AnalysisState) -> Dict[str, Any]:
    """Generate final analysis result."""
    logger.info("---GENERATE FINAL ANALYSIS---")
    try:
        messages: List[Any] = state.get("messages", [])
        trend_analysis: str = state.get("trend_analysis", "")
        opportunity_analysis: str = state.get("opportunity_analysis", "")
        competitor_analysis: str = state.get("competitor_analysis", "")
        
        prompt: PromptTemplate = PromptTemplate(
            template=config.get("prompts", {}).get("final_analysis", ""),
            input_variables=["trend_analysis", "opportunity_analysis", "competitor_analysis", "user_input"]
        )
        
        new_messages: List[Any] = [
            SystemMessage(content=prompt.format(
                trend_analysis=trend_analysis,
                opportunity_analysis=opportunity_analysis,
                competitor_analysis=competitor_analysis,
                user_input=messages[0].content if messages else ""
            )),
            messages[0] if messages else HumanMessage(content="")
        ]
        
        response: Any = model.invoke(new_messages)
        logger.debug(f"Final analysis response: {response.content}")
        
        new_state = state.copy()
        new_state["messages"] = [*messages, response]
        new_state["final_analysis"] = response.content
        new_state["next"] = END
        
        return new_state

    except Exception as e:
        logger.error(f"Error in final analysis: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"next": END, "error": str(e)}

def extract_trends_from_message(message_content: str) -> List[Dict[str, Any]]:
    """Extract trends from message content with improved parsing and validation."""
    logger.debug(f"Extracting trends from message: {message_content[:200]}...")
    
    try:
        # Parse the JSON content first
        content = json.loads(message_content)
        if not isinstance(content, dict) or "trends" not in content:
            logger.warning("Message content does not contain trends key")
            return [{"content": message_content, "type": "raw_content"}]
            
        # Filter out incomplete trends
        valid_trends = []
        required_fields = {
            "name", "description", "Year_2025", "Year_2026", "Year_2027",
            "Year_2028", "Year_2029", "Year_2030", "Startup_Opportunity",
            "Growth_rate_WoW", "YC_chances", "Related_trends"
        }
        
        for trend in content["trends"]:
            if all(field in trend for field in required_fields):
                valid_trends.append(trend)
            else:
                logger.warning(f"Skipping incomplete trend: {trend.get('name', 'unknown')}")
                
        if not valid_trends:
            logger.warning("No valid trends found after filtering")
            return [{"content": message_content, "type": "raw_content"}]
            
        logger.info(f"Successfully extracted {len(valid_trends)} valid trends")
        return valid_trends
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON content: {str(e)}")
        return [{"content": message_content, "type": "raw_content"}]
    except Exception as e:
        logger.error(f"Unexpected error in trend extraction: {str(e)}")
        return [{"content": message_content, "type": "raw_content"}]

def generate_final_result(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate final analysis result using KTrendOps parser."""
    logger.info("---GENERATE FINAL ANALYSIS---")
    try:
        messages: List[Any] = state.get("messages", [])
        if not messages:
            logger.error("No messages found in state")
            return {"error": "No messages found in state"}

        # Initialize KTrendOps parser
        trend_parser = PydanticOutputParser(pydantic_object=KTrendOps)
        format_instructions = trend_parser.get_format_instructions()

        # Get prompt from config
        prompt = PromptTemplate(
            template=config.get("prompts", {}).get("bi_report", ""),
            input_variables=["format_instructions", "messages"]
        )

        # Create final analysis message
        final_message = SystemMessage(content=prompt.format(
            format_instructions=format_instructions,
            messages=messages[-1].content if hasattr(messages[-1], 'content') else json.dumps(messages[-1])
        ))

        # Get response
        response = model.invoke([*messages, final_message])
        logger.debug(f"Final analysis response: {response.content}")

        try:
            # Parse response using KTrendOps
            parsed_content = trend_parser.parse(response.content)
            
            # Convert trends to list of dicts using Pydantic's dict() method
            return {
                "trends": [trend.dict(exclude_none=True) for trend in parsed_content.trends]
            }

        except Exception as e:
            logger.error(f"Error parsing final analysis: {str(e)}")
            return {"error": f"Error parsing final analysis: {str(e)}"}

    except Exception as e:
        logger.error(f"Error in generate_final: {str(e)}")
        return {"error": f"Error in generate_final: {str(e)}"}

def save_analysis_result(result: Dict[str, Any], focus_area: str) -> None:
    """Save analysis result to file."""
    try:
        logger.debug("Starting save_analysis_result")
        logger.debug(f"Result keys: {result.keys()}")
        
        # Create results directory if it doesn't exist
        results_dir = os.path.join(os.path.dirname(__file__), "results")
        os.makedirs(results_dir, exist_ok=True)
        
        # Generate filename with timestamp and focus area
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{focus_area.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}.json"
        filepath = os.path.join(results_dir, filename)
        
        logger.debug(f"Saving to file: {filepath}")
        with open(filepath, 'w') as f:
            json.dump(result, f, indent=2)
        logger.info(f"Successfully saved analysis result to {filepath}")
        
    except Exception as e:
        logger.error(f"Error saving analysis result: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

# Define workflow graph
workflow: StateGraph = StateGraph(AnalysisState)

# Add nodes
workflow.add_node("analyze", _analyze_trends)
workflow.add_node("opportunities", analyze_opportunities)
workflow.add_node("competitors", analyze_competitors)
workflow.add_node("generate", generate_final)

# Add edges
workflow.add_edge(START, "analyze")

# Add conditional edges after trend analysis
workflow.add_conditional_edges(
    "analyze",
    check_analysis_quality,
    {
        "analyze_trends": "analyze",
        "analyze_opportunities": "opportunities"
    }
)

# Add remaining edges
workflow.add_edge("opportunities", "competitors")
workflow.add_edge("competitors", "generate")
workflow.add_edge("generate", END)

# Compile graph
graph: StateGraph = workflow.compile()

async def run_analysis(user_input: str, focus_area: str, generate_novel: bool = True, k: int = 10) -> str:
    """Run the multi-step analysis process using the state graph."""
    try:
        # Ensure k is a valid integer at the start
        try:
            k = max(1, min(50, int(k)))
        except (TypeError, ValueError):
            logger.warning(f"Invalid k value: {k}, using default k=10")
            k = 10
            
        logger.info(f"Starting analysis for focus_area='{focus_area}', k={k}")
        logger.debug(f"User input: {user_input}")
        
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "focus_area": focus_area,
            "user_input": user_input,
            "trend_analysis": "",
            "opportunity_analysis": "",
            "competitor_analysis": "",
            "final_analysis": "",
            "current_step": 0,
            "trends": [],
            "k": k,
            "retry_count": 0
        }
        
        # Call analyze_trends and return response
        return await _analyze_trends(initial_state)
        
    except Exception as e:
        logger.error(f"Error in run_analysis: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
