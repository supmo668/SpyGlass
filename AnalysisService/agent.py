from typing import Annotated, Literal, Sequence, TypedDict, List, Dict, Any, Optional, Union
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_together import ChatTogether
from langchain.output_parsers import PydanticOutputParser
from langgraph.graph import END, StateGraph, START
import logging
import traceback
import yaml
import os
from datetime import datetime
from models import (
    TrendOp,
    KTrendOps,
    AnalysisInput,
    StartupAnalysisResponse,
    IntermediateStep,
    IntermediateResults
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

class AnalysisState(TypedDict):
    """Type definition for analysis state."""
    messages: List[BaseMessage]
    user_input: str
    k: int
    intermediate_results: IntermediateResults
    final_result: Optional[StartupAnalysisResponse]

def create_chat_model() -> ChatTogether:
    """Create a ChatTogether model instance with error handling."""
    try:
        return ChatTogether(
            model=config["model"]["name"],
            temperature=config["model"]["temperature"],
            max_tokens=config["model"]["max_tokens"],
            together_api_key=os.environ['TOGETHERAI_API_KEY'],
            base_url=config["model"]["base_url"],
            max_retries=2,
            timeout=120
        )
    except Exception as e:
        logger.error(f"Failed to initialize ChatTogether model: {e}")
        raise RuntimeError("Failed to initialize language model") from e

async def trend_analysis(state: AnalysisState) -> Dict[str, Any]:
    """Analyze trends based on user input."""
    try:
        chat_model = create_chat_model()
        trend_parser = PydanticOutputParser(pydantic_object=KTrendOps)
        format_instructions = trend_parser.get_format_instructions()
        
        prompt = PromptTemplate(
            template=config["prompts"]["trend_analysis"],
            input_variables=["format_instructions", "user_input", "k"]
        )
        
        messages = [
            SystemMessage(content=config["prompts"]["system"]),
            HumanMessage(content=prompt.format(
                format_instructions=format_instructions,
                user_input=state["user_input"],
                k=state["k"]
            ))
        ]
        
        response = await chat_model.ainvoke(messages)
        
        # Create intermediate step
        is_refined = state["intermediate_results"].trend_analysis is not None
        refinement_count = state["intermediate_results"].trend_analysis.refinement_count + 1 if state["intermediate_results"].trend_analysis else 0
        
        step = IntermediateStep(
            step_name="trend_analysis",
            output=response.content,
            timestamp=datetime.now().isoformat(),
            is_refined=is_refined,
            refinement_count=refinement_count
        )
        
        # Update state
        state["intermediate_results"].trend_analysis = step
        if is_refined:
            state["intermediate_results"].refinement_steps.append(step)
            
        return {"messages": messages + [response], "intermediate_results": state["intermediate_results"]}
        
    except Exception as e:
        logger.error(f"Error in trend analysis: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

async def opportunity_analysis(state: AnalysisState) -> Dict[str, Any]:
    """Analyze opportunities based on trends."""
    try:
        chat_model = create_chat_model()
        messages = state["messages"]
        trend_analysis = state["intermediate_results"].trend_analysis
        if not trend_analysis:
            raise ValueError("No trend analysis results found")
            
        prompt = PromptTemplate(
            template=config["prompts"]["opportunity_analysis"],
            input_variables=["trend_analysis", "user_input"]
        )
        
        new_message = HumanMessage(content=prompt.format(
            trend_analysis=trend_analysis.output,
            user_input=state["user_input"]
        ))
        
        response = await chat_model.ainvoke([SystemMessage(content=config["prompts"]["system"]), new_message])
        
        # Create intermediate step
        is_refined = state["intermediate_results"].opportunity_analysis is not None
        refinement_count = state["intermediate_results"].opportunity_analysis.refinement_count + 1 if state["intermediate_results"].opportunity_analysis else 0
        
        step = IntermediateStep(
            step_name="opportunity_analysis",
            output=response.content,
            timestamp=datetime.now().isoformat(),
            is_refined=is_refined,
            refinement_count=refinement_count
        )
        
        # Update state
        state["intermediate_results"].opportunity_analysis = step
        if is_refined:
            state["intermediate_results"].refinement_steps.append(step)
            
        return {"messages": messages + [response], "intermediate_results": state["intermediate_results"]}
        
    except Exception as e:
        logger.error(f"Error in opportunity analysis: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

async def competitor_analysis(state: AnalysisState) -> Dict[str, Any]:
    """Analyze competitors based on opportunities."""
    try:
        chat_model = create_chat_model()
        messages = state["messages"]
        opportunity_analysis = state["intermediate_results"].opportunity_analysis
        if not opportunity_analysis:
            raise ValueError("No opportunity analysis results found")
            
        prompt = PromptTemplate(
            template=config["prompts"]["competitor_analysis"],
            input_variables=["opportunity_analysis", "user_input"]
        )
        
        new_message = HumanMessage(content=prompt.format(
            opportunity_analysis=opportunity_analysis.output,
            user_input=state["user_input"]
        ))
        
        response = await chat_model.ainvoke([SystemMessage(content=config["prompts"]["system"]), new_message])
        
        # Create intermediate step
        is_refined = state["intermediate_results"].competitor_analysis is not None
        refinement_count = state["intermediate_results"].competitor_analysis.refinement_count + 1 if state["intermediate_results"].competitor_analysis else 0
        
        step = IntermediateStep(
            step_name="competitor_analysis",
            output=response.content,
            timestamp=datetime.now().isoformat(),
            is_refined=is_refined,
            refinement_count=refinement_count
        )
        
        # Update state
        state["intermediate_results"].competitor_analysis = step
        if is_refined:
            state["intermediate_results"].refinement_steps.append(step)
            
        return {"messages": messages + [response], "intermediate_results": state["intermediate_results"]}
        
    except Exception as e:
        logger.error(f"Error in competitor analysis: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

async def generate_final_result(state: AnalysisState) -> Dict[str, Any]:
    """Generate final analysis result."""
    try:
        # Get trend analysis output
        trend_analysis_step = state["intermediate_results"].trend_analysis
        if not trend_analysis_step:
            raise ValueError("No trend analysis results found")
            
        # Parse the trend analysis into StartupAnalysisResponse
        parser = PydanticOutputParser(pydantic_object=StartupAnalysisResponse)
        final_result = parser.parse(trend_analysis_step.output)
        
        state["final_result"] = final_result
        return {
            "messages": state["messages"],
            "intermediate_results": state["intermediate_results"],
            "final_result": final_result
        }
        
    except Exception as e:
        logger.error(f"Error in generate final result: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def check_quality(state: AnalysisState) -> Literal["refine", "continue"]:
    """Check quality of current analysis step."""
    try:
        messages = state["messages"]
        last_message = messages[-1].content if messages else ""
        
        # Simple validation: check if the response is too short
        if len(last_message) < 100:
            logger.warning("Analysis response too short, requesting refinement")
            return "refine"
        
        return "continue"
        
    except Exception as e:
        logger.error(f"Error in quality check: {e}")
        return "continue"  # Continue on error to avoid loops

async def run_analysis(query: AnalysisInput) -> IntermediateResults:
    """Run the complete analysis workflow and return all intermediate results."""
    try:
        start_time = datetime.now()
        
        # Initialize state and results
        intermediate_results = IntermediateResults(
            trend_analysis=None,
            opportunity_analysis=None,
            competitor_analysis=None,
            final_result=None,
            execution_time=0.0,
            refinement_steps=[]
        )
        
        state = AnalysisState(
            messages=[],
            user_input=query.user_input,
            k=query.k,
            intermediate_results=intermediate_results,
            final_result=None
        )
        
        # Define workflow
        workflow = StateGraph(AnalysisState)
        
        # Add nodes
        workflow.add_node("trends", trend_analysis)
        workflow.add_node("opportunities", opportunity_analysis)
        workflow.add_node("competitors", competitor_analysis)
        workflow.add_node("generate", generate_final_result)
        
        # Add edges with quality checks
        workflow.add_edge(START, "trends")
        workflow.add_conditional_edges(
            "trends",
            check_quality,
            {
                "refine": "trends",
                "continue": "opportunities"
            }
        )
        workflow.add_conditional_edges(
            "opportunities",
            check_quality,
            {
                "refine": "opportunities",
                "continue": "competitors"
            }
        )
        workflow.add_edge("competitors", "generate")
        workflow.add_edge("generate", END)
        
        # Compile and run
        graph = workflow.compile()
        final_state = await graph.ainvoke(state)
        
        # Calculate execution time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Update final results
        final_results = IntermediateResults(
            trend_analysis=final_state["intermediate_results"].trend_analysis,
            opportunity_analysis=final_state["intermediate_results"].opportunity_analysis,
            competitor_analysis=final_state["intermediate_results"].competitor_analysis,
            final_result=final_state.get("final_result"),
            execution_time=execution_time,
            refinement_steps=final_state["intermediate_results"].refinement_steps
        )
        
        return final_results
            
    except Exception as e:
        logger.error(f"Error in run_analysis: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
