from typing import List, Dict, Any, TypedDict, Annotated
from langchain_core.prompts import ChatPromptTemplate
from langchain_together import ChatTogether
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode
import yaml
import os
import logging
import traceback
from datetime import datetime
from tools import ApertureTools
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # Load configuration
    logger.info("Loading configuration from config.yaml")
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
except Exception as e:
    logger.error(f"Failed to load config.yaml: {str(e)}")
    raise

try:
    # Initialize ApertureDB tools
    logger.info("Initializing ApertureDB tools")
    aperture_tools = ApertureTools()

    # Initialize the LLM with TogetherAI
    logger.info("Initializing TogetherAI model")
    model = ChatTogether(
        model=config["model"]["name"],
        temperature=config["model"]["temperature"],
        max_tokens=config["model"]["max_tokens"],
        together_api_key=os.environ['TOGETHERAI_API_KEY'],
        max_retries=2,
        timeout=120  # 2 minute timeout
    )

    # Get the retriever tool
    logger.info("Getting retriever tool")
    tools = [aperture_tools.get_tool()]
except Exception as e:
    logger.error(f"Failed to initialize components: {str(e)}")
    raise

class TrendOp(BaseModel):
    """Model for a trend operation analysis."""
    Trend: str = Field(description="Name of the trend")
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

# Initialize the output parser
trend_parser = PydanticOutputParser(pydantic_object=TrendOp)

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

def trend_analysis(state: AnalysisState) -> AnalysisState:
    """Analyze trends in the focus area."""
    try:
        logger.info("Starting trend analysis")
        
        # Add format instructions from the TrendOp parser
        format_instructions = trend_parser.get_format_instructions()
        
        messages = [
            SystemMessage(content=f"""You are a trend analysis expert. Analyze the following business opportunity or focus area:
{state['focus_area']}
{state['user_input']}

Provide your analysis in the exact format specified below:
{format_instructions}

Remember to:
1. Express all percentages as decimals (0.0 to 1.0)
2. Make realistic projections for each year
3. Estimate growth rates and YC chances based on market data
"""),
            HumanMessage(content=f"""
            Focus Area: {state['focus_area']}
            User Input: {state['user_input']}
            
            Please analyze trends in this area. Use the search_business_reports tool to find relevant market data and trend information.
            
            {config["prompts"]["steps"][0]["instruction"]}
            """)
        ]
        
        model_with_tools = model.bind_tools(tools)
        response = model_with_tools.invoke(messages)
        state["trend_analysis"] = response.content
        state["messages"].append(response)
        state["current_step"] = 1
        
        logger.info("Completed trend analysis")
        logger.debug(f"Updated state: current_step={state['current_step']}")
        return state
    except Exception as e:
        logger.error(f"Error in trend analysis: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def opportunity_analysis(state: AnalysisState) -> AnalysisState:
    """Analyze business opportunities based on trends."""
    try:
        logger.info("Starting opportunity analysis")
        logger.debug(f"Input state: trend_analysis length={len(state['trend_analysis'])}")
        
        messages = [
            SystemMessage(content=config["prompts"]["system"]),
            HumanMessage(content=f"""
            Focus Area: {state['focus_area']}
            Previous Analysis: {state['trend_analysis']}
            
            Based on the trend analysis above, analyze business opportunities. Use the search_business_reports tool to find similar opportunities and market analyses.
            
            {config["prompts"]["steps"][1]["instruction"]}
            """)
        ]
        
        model_with_tools = model.bind_tools(tools)
        response = model_with_tools.invoke(messages)
        state["opportunity_analysis"] = response.content
        state["messages"].append(response)
        state["current_step"] = 2
        
        logger.info("Completed opportunity analysis")
        logger.debug(f"Updated state: current_step={state['current_step']}")
        return state
    except Exception as e:
        logger.error(f"Error in opportunity analysis: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def competitor_analysis(state: AnalysisState) -> AnalysisState:
    """Analyze competitors based on opportunities."""
    try:
        logger.info("Starting competitor analysis")
        logger.debug(f"Input state: opportunity_analysis length={len(state['opportunity_analysis'])}")
        
        messages = [
            SystemMessage(content=config["prompts"]["system"]),
            HumanMessage(content=f"""
            Focus Area: {state['focus_area']}
            Previous Analyses:
            Trends: {state['trend_analysis']}
            Opportunities: {state['opportunity_analysis']}
            
            Based on the analyses above, analyze competitors. Use the search_business_reports tool to find information about existing companies and their market positions.
            
            {config["prompts"]["steps"][2]["instruction"]}
            """)
        ]
        
        model_with_tools = model.bind_tools(tools)
        response = model_with_tools.invoke(messages)
        state["competitor_analysis"] = response.content
        state["messages"].append(response)
        state["current_step"] = 3
        
        logger.info("Completed competitor analysis")
        logger.debug(f"Updated state: current_step={state['current_step']}")
        return state
    except Exception as e:
        logger.error(f"Error in competitor analysis: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def final_analysis(state: AnalysisState) -> AnalysisState:
    """Generate final comprehensive analysis."""
    try:
        logger.info("Starting final analysis")
        logger.debug(f"Input state: competitor_analysis length={len(state['competitor_analysis'])}")
        
        messages = [
            SystemMessage(content=config["prompts"]["system"]),
            HumanMessage(content=f"""
            Focus Area: {state['focus_area']}
            Previous Analyses:
            Trends: {state['trend_analysis']}
            Opportunities: {state['opportunity_analysis']}
            Competitors: {state['competitor_analysis']}
            
            Compile a final comprehensive analysis. Use the search_business_reports tool to find additional supporting data for your conclusions.
            
            {config["prompts"]["steps"][3]["instruction"]}
            """)
        ]
        
        model_with_tools = model.bind_tools(tools)
        response = model_with_tools.invoke(messages)
        state["final_analysis"] = response.content
        state["messages"].append(response)
        state["current_step"] = 4
        
        logger.info("Completed final analysis")
        logger.debug(f"Updated state: current_step={state['current_step']}")
        return state
    except Exception as e:
        logger.error(f"Error in final analysis: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def should_continue(state: AnalysisState) -> str:
    """Determine next step based on current state."""
    try:
        logger.debug(f"Checking next step for current_step={state['current_step']}")
        step = state['current_step']
        if step == 0:
            return "opportunity"
        elif step == 1:
            return "competitor"
        elif step == 2:
            return "final"
        else:
            return "end"
    except Exception as e:
        logger.error(f"Error in should_continue: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

try:
    logger.info("Creating workflow graph")
    # Create the workflow graph
    workflow = StateGraph(AnalysisState)

    # Add nodes for each analysis step
    workflow.add_node("trend", trend_analysis)
    workflow.add_node("opportunity", opportunity_analysis)
    workflow.add_node("competitor", competitor_analysis)
    workflow.add_node("final", final_analysis)

    # Define the workflow
    workflow.add_edge(START, "trend")
    workflow.add_conditional_edges(
        "trend",
        should_continue,
        {
            "opportunity": "opportunity",
            "competitor": "competitor",
            "final": "final",
            "end": END
        }
    )
    workflow.add_conditional_edges(
        "opportunity",
        should_continue,
        {
            "competitor": "competitor",
            "final": "final",
            "end": END
        }
    )
    workflow.add_conditional_edges(
        "competitor",
        should_continue,
        {
            "final": "final",
            "end": END
        }
    )
    workflow.add_edge("final", END)

    # Compile the graph
    logger.info("Compiling workflow graph")
    graph = workflow.compile()
except Exception as e:
    logger.error(f"Failed to create or compile workflow graph: {str(e)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    raise

def extract_percentage(text: str) -> float:
    """Extract percentage value from text and convert to float."""
    try:
        # Remove % sign and convert to float
        return float(text.strip().rstrip('%')) / 100
    except (ValueError, AttributeError):
        return 0.0

def generate_year_projections(growth_rate: float, base_year: float = None) -> Dict[str, float]:
    """Generate year-by-year projections based on growth rate."""
    if base_year is None:
        base_year = 0.2  # Start at 20% if no base provided
    
    years = {}
    current = base_year
    for year in range(2025, 2031):
        years[f"year_{year}"] = min(current, 1.0)  # Cap at 100%
        current = current * (1 + growth_rate)
    
    return years

async def run_analysis(user_input: str, focus_area: str, generate_novel: bool = True, k: int = 10) -> Dict[str, Any]:
    """Run the multi-step analysis process using the state graph."""
    try:
        logger.info(f"Starting analysis for focus_area='{focus_area}', k={k}")
        logger.debug(f"User input: {user_input}")
        
        # Initialize state
        initial_state = AnalysisState(
            messages=[],
            focus_area=focus_area,
            user_input=user_input,
            trend_analysis="",
            opportunity_analysis="",
            competitor_analysis="",
            final_analysis="",
            current_step=0,
            trends=[]
        )
        
        # Run the graph
        logger.info("Invoking workflow graph")
        final_state = await graph.ainvoke(initial_state)
        logger.info("Workflow graph execution completed")
        
        # Parse trends using the TrendOp parser
        try:
            logger.info("Parsing trends from analysis")
            trends = []
            
            # Split the analysis into individual trend sections
            trend_sections = final_state["trend_analysis"].split("\n\n")
            
            for section in trend_sections:
                if section.strip():
                    try:
                        # Parse the trend section using the TrendOp parser
                        trend = trend_parser.parse(section)
                        trends.append(trend.dict())
                    except Exception as e:
                        logger.error(f"Error parsing trend section: {str(e)}")
                        continue
            
            # Sort trends by YC chances and growth rate
            trends.sort(key=lambda x: (x.get("YC_chances", 0), x.get("Growth_rate_WoW", 0)), reverse=True)
            
            # Take top k trends
            final_state["trends"] = trends[:k]
            logger.info(f"Parsed {len(final_state['trends'])} trends (top {k})")
            
        except Exception as e:
            logger.error(f"Error parsing trends: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            final_state["trends"] = []
        
        # Store the analysis in ApertureDB if generating novel ideas
        if generate_novel:
            try:
                logger.info("Storing analysis in ApertureDB")
                document = Document(
                    page_content=f"""
                    Focus Area: {focus_area}
                    User Input: {user_input}
                    
                    Trend Analysis:
                    {final_state['trend_analysis']}
                    
                    Opportunity Analysis:
                    {final_state['opportunity_analysis']}
                    
                    Competitor Analysis:
                    {final_state['competitor_analysis']}
                    
                    Final Analysis:
                    {final_state['final_analysis']}
                    """,
                    metadata={
                        "type": "business_analysis",
                        "focus_area": focus_area,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                await aperture_tools.add_document(document)
                logger.info("Successfully stored analysis in ApertureDB")
            except Exception as e:
                logger.error(f"Failed to store analysis in ApertureDB: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
        
        return {
            "trend_analysis": final_state["trend_analysis"],
            "opportunity_analysis": final_state["opportunity_analysis"],
            "competitor_analysis": final_state["competitor_analysis"],
            "final_analysis": final_state["final_analysis"],
            "trends": final_state["trends"]
        }
    except Exception as e:
        logger.error(f"Error in run_analysis: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
