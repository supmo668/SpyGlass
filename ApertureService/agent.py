from typing import Annotated, Literal, Sequence, TypedDict, List, Dict, Any, Optional
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

def check_analysis_quality(state: AnalysisState) -> Literal["generate", "refine"]:
    """
    Check if the analysis quality is sufficient or needs refinement.
    Limits retries to prevent infinite recursion.
    """
    logger.debug("---CHECK ANALYSIS QUALITY---")
    
    try:
        messages: List[Any] = state["messages"]
        last_message: Any = messages[-1]
        analysis: str = last_message.content
        retry_count: int = state.get("retry_count", 0)
        
        # Check retry limit
        if retry_count >= 3:
            logger.warning("Reached retry limit, proceeding with current analysis")
            return "generate"
        
        # Check if we have valid trends
        if not analysis:
            logger.debug("No analysis found, but proceeding due to retry limit")
            return "generate"
        
        # Try parsing trends
        try:
            trend_parser: PydanticOutputParser = PydanticOutputParser(pydantic_object=KTrendOps)
            parsed: KTrendOps = trend_parser.parse(analysis)
            if parsed and parsed.trends:
                logger.debug(f"Successfully parsed {len(parsed.trends)} trends")
                return "generate"
        except Exception as e:
            logger.debug(f"Failed to parse trends: {str(e)}")
        
        # Increment retry count
        state["retry_count"] = retry_count + 1
        
        if retry_count < 2:  # Allow 2 retries
            logger.debug(f"Requesting refinement (retry {retry_count + 1}/3)")
            return "refine"
        else:
            logger.warning("Max retries reached, proceeding with current analysis")
            return "generate"
            
    except Exception as e:
        logger.error(f"Error in quality check: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return "generate"  # On error, proceed rather than retry

def analyze_trends(state: AnalysisState) -> AnalysisState:
    """
    Initial trend analysis step.
    """
    logger.info("---ANALYZE TRENDS---")
    try:
        messages: List[Any] = state["messages"]
        k: int = state.get("k", 10)  # Get k from state
        
        # Get format instructions for k trends
        trend_parser: PydanticOutputParser = PydanticOutputParser(pydantic_object=KTrendOps)
        format_instructions: str = trend_parser.get_format_instructions()
        
        # Get prompt from config
        prompt: PromptTemplate = PromptTemplate(
            template=config.get("prompts", {}).get("trend_analysis", ""),
            input_variables=["user_input", "format_instructions", "k"]
        )
        
        # Create messages
        new_messages: List[Any] = [
            SystemMessage(content=prompt.format(
                user_input=messages[0].content,
                format_instructions=format_instructions,
                k=k
            )),
            messages[0]  # Original user message
        ]
        
        # Get response
        response: Any = model.invoke(new_messages)
        logger.debug(f"Trend analysis response: {response.content}")
        
        # Initialize retry count in state
        if "retry_count" not in state:
            state["retry_count"] = 0
        
        return {"messages": [*messages, response], "retry_count": state["retry_count"]}
        
    except Exception as e:
        logger.error(f"Error in trend analysis: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Return empty response rather than failing
        return {"messages": [*messages, SystemMessage(content="")], "retry_count": state.get("retry_count", 0)}

def analyze_opportunities(state: AnalysisState) -> AnalysisState:
    """
    Analyze opportunities based on trends.
    """
    logger.info("---ANALYZE OPPORTUNITIES---")
    try:
        messages: List[Any] = state["messages"]
        last_message: Any = messages[-1]  # Trend analysis
        
        prompt: PromptTemplate = PromptTemplate(
            template=config.get("prompts", {}).get("opportunity_analysis", ""),
            input_variables=["trend_analysis", "user_input"]
        )
        
        new_messages: List[Any] = [
            SystemMessage(content=prompt.format(
                trend_analysis=last_message.content,
                user_input=messages[0].content
            )),
            messages[0]  # Original user message
        ]
        
        response: Any = model.invoke(new_messages)
        logger.debug(f"Opportunity analysis response: {response.content}")
        
        return {"messages": [*messages, response]}
        
    except Exception as e:
        logger.error(f"Error in opportunity analysis: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def analyze_competitors(state: AnalysisState) -> AnalysisState:
    """
    Analyze competitors based on opportunities.
    """
    logger.info("---ANALYZE COMPETITORS---")
    try:
        messages: List[Any] = state["messages"]
        opportunity_message: Any = messages[-1]
        trend_message: Any = messages[-2]
        
        prompt: PromptTemplate = PromptTemplate(
            template=config.get("prompts", {}).get("competitor_analysis", ""),
            input_variables=["opportunity_analysis", "user_input"]
        )
        
        new_messages: List[Any] = [
            SystemMessage(content=prompt.format(
                opportunity_analysis=opportunity_message.content,
                user_input=messages[0].content
            )),
            messages[0]  # Original user message
        ]
        
        response: Any = model.invoke(new_messages)
        logger.debug(f"Competitor analysis response: {response.content}")
        
        return {"messages": [*messages, response]}
        
    except Exception as e:
        logger.error(f"Error in competitor analysis: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def extract_trends_from_message(message_content: str) -> List[Dict[str, Any]]:
    """Extract trends from message content with improved logging and fallback handling."""
    logger.debug(f"Extracting trends from message: {message_content[:200]}...")
    
    try:
        # Try parsing with KTrendOps
        parsed_content = KTrendOps.parse_raw(message_content)
        trends = parsed_content.trends
        
        if not trends:
            logger.warning("KTrendOps parsing succeeded but returned empty trends")
            return [{"content": message_content, "type": "raw_content"}]
            
        logger.info(f"Successfully extracted {len(trends)} trends")
        return trends
        
    except Exception as e:
        logger.error(f"Failed to parse trends with KTrendOps: {str(e)}")
        # Fallback: Return the raw message content as a trend
        return [{"content": message_content, "type": "raw_content"}]

def generate_final(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate final analysis result."""
    try:
        logger.debug("Starting generate_final")
        messages = state.get("messages", [])
        
        # Debug log the messages
        logger.debug(f"Number of messages to process: {len(messages)}")
        for i, msg in enumerate(messages):
            logger.debug(f"Message {i} type: {type(msg)}")
            logger.debug(f"Message {i} content: {msg.content if hasattr(msg, 'content') else 'No content'}")
        
        # Convert messages to serializable format
        serializable_messages = [
            {
                "role": msg.type if hasattr(msg, 'type') else 'unknown',
                "content": msg.content if hasattr(msg, 'content') else '',
                "additional_kwargs": msg.additional_kwargs if hasattr(msg, 'additional_kwargs') else {}
            }
            for msg in messages
            if hasattr(msg, 'type') and hasattr(msg, 'content')
        ]
        
        # Extract trends from the first AI message (trend analysis)
        trends = []
        for msg in messages:
            if hasattr(msg, 'type') and msg.type == 'ai':
                trends = extract_trends_from_message(msg.content)
                if trends:
                    break
        
        logger.debug(f"Extracted {len(trends)} trends")
        
        result = {
            "messages": serializable_messages,
            "trends": trends,
            "trend_analysis": state.get("trend_analysis", ""),
            "opportunity_analysis": state.get("opportunity_analysis", ""),
            "competitor_analysis": state.get("competitor_analysis", ""),
            "final_analysis": state.get("final_analysis", "")
        }
        
        logger.debug("Saving analysis result")
        save_analysis_result(result, state.get("focus_area", "business_opportunities"))
        logger.info("Successfully generated and saved final analysis")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in generate_final: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "messages": [],
            "trends": [],
            "trend_analysis": f"Error during analysis: {str(e)}",
            "opportunity_analysis": "Error during analysis",
            "competitor_analysis": "Error during analysis",
            "final_analysis": "Error during analysis"
        }

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
workflow.add_node("analyze", analyze_trends)
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
        "generate": "opportunities",
        "refine": "analyze"
    }
)

# Add remaining edges
workflow.add_edge("opportunities", "competitors")
workflow.add_edge("competitors", "generate")
workflow.add_edge("generate", END)

# Compile graph
graph: StateGraph = workflow.compile()

async def run_analysis(user_input: str, focus_area: str, generate_novel: bool = True, k: int = 10) -> Dict[str, Any]:
    """Run the multi-step analysis process using the state graph."""
    try:
        # Ensure k is a valid integer at the start
        try:
            k: int = max(1, min(50, int(k)))
        except (TypeError, ValueError):
            logger.warning(f"Invalid k value: {k}, using default k=10")
            k = 10
            
        logger.info(f"Starting analysis for focus_area='{focus_area}', k={k}")
        logger.debug(f"User input: {user_input}")
        
        # Initialize state
        initial_state: Dict[str, Any] = {
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
        
        # Create results directory if it doesn't exist
        results_dir: str = os.path.join(os.path.dirname(__file__), "results")
        os.makedirs(results_dir, exist_ok=True)
        
        # Generate unique run ID
        timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_id: str = uuid.uuid4().hex[:8]
        
        # Initialize results dictionary
        run_results: Dict[str, Any] = {
            "run_id": run_id,
            "timestamp": timestamp,
            "focus_area": focus_area,
            "user_input": user_input,
            "k": k,
            "steps": [],
            "final_output": None
        }
        
        # Run the graph
        logger.info("Invoking workflow graph")
        final_output: Optional[Dict[str, Any]] = None
        
        # Stream and log outputs
        for output in graph.stream(initial_state):
            for key, value in output.items():
                logger.debug(f"Output from node '{key}':")
                logger.debug(value)
                
                # Save intermediate result with serializable message content
                step_result: Dict[str, Any] = {
                    "step": key,
                    "output": {}
                }
                
                if isinstance(value, dict):
                    serializable_value = {}
                    for k_val, v in value.items():
                        if k_val == "messages":
                            # Extract content and metadata from LangChain messages
                            serializable_value[k_val] = [
                                {
                                    "role": msg.type if hasattr(msg, 'type') else 'unknown',
                                    "content": msg.content if hasattr(msg, 'content') else '',
                                    "additional_kwargs": msg.additional_kwargs if hasattr(msg, 'additional_kwargs') else {}
                                }
                                for msg in v if hasattr(msg, 'type') and hasattr(msg, 'content')
                            ]
                        else:
                            serializable_value[k_val] = v
                    step_result["output"] = serializable_value
                
                run_results["steps"].append(step_result)
                final_output = value
        
        logger.info("Workflow graph execution completed")
        
        if not final_output:
            logger.error("No final output generated from graph")
            return {"error": "No output generated"}
            
        trends = []
        for msg in final_output.get("messages", []):
            if msg.get("content"):
                extracted_trends = extract_trends_from_message(msg["content"])
                if extracted_trends:
                    trends.extend(extracted_trends)
        
        if not trends:
            logger.warning("No trends extracted from any messages")
            # Include the last message content if no trends were extracted
            last_message = next((msg["content"] for msg in reversed(final_output.get("messages", [])) if msg.get("content")), None)
            if last_message:
                trends = [{"content": last_message, "type": "raw_content"}]
        
        logger.info(f"Analysis completed with {len(trends)} trends")
        return {
            "messages": final_output.get("messages", []),
            "trends": trends
        }
        
    except Exception as e:
        logger.error(f"Error in run_analysis: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
