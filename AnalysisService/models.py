from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, field_validator

class TrendOp(BaseModel):
    """Model for a trend operation analysis."""
    name: str = Field(description="Name of the trend/domain that the startup is related to")
    description: str = Field(description="Description of the trend and its impact on the market")
    Year_2025: int = Field(description="Annual growth/adoption rate for 2025 as integer percentage (1-100)", gt=0)
    Year_2026: int = Field(description="Annual growth/adoption rate for 2026 as integer percentage (1-100)", gt=0)
    Year_2027: int = Field(description="Annual growth/adoption rate for 2027 as integer percentage (1-100)", gt=0)
    Year_2028: int = Field(description="Annual growth/adoption rate for 2028 as integer percentage (1-100)", gt=0)
    Year_2029: int = Field(description="Annual growth/adoption rate for 2029 as integer percentage (1-100)", gt=0)
    Year_2030: int = Field(description="Annual growth/adoption rate for 2030 as integer percentage (1-100)", gt=0)
    Startup_Name: str = Field(description="Catchy and descriptive name for the startup opportunity")
    Startup_Opportunity: str = Field(description="Detailed description of the startup opportunity, including how it leverages the trends")
    Growth_rate_WoW: float = Field(description="Percentage of Week-over-week growth between 0 and 100 (>50 for YC qualification)", ge=0)
    YC_chances: float = Field(description="Percentage of probability of YC acceptance based on uniqueness and growth potential of the start-up in percentage between 0 to 100", ge=0.0, le=100.0)
    Related_trends: str = Field(description="Comma-separated list of related trends that the startup leverages")

    @field_validator('Year_2025', 'Year_2026', 'Year_2027', 'Year_2028', 'Year_2029', 'Year_2030')
    @classmethod
    def validate_year(cls, v: int) -> int:
        if v > 100:
            raise ValueError('Year percentage must be less than or equal to 100')
        return v

    model_config = {
        'json_schema_extra': {
            'examples': [{
                'name': 'Remote Work Tools',
                'description': 'Demand for advanced remote work tools',
                'Year_2025': 65,
                'Year_2026': 72,
                'Year_2027': 81,
                'Year_2028': 88,
                'Year_2029': 92,
                'Year_2030': 96,
                'Startup_Name': 'WorkFlow AI',
                'Startup_Opportunity': 'Create user-friendly, secure remote work platforms',
                'Growth_rate_WoW': 7,
                'YC_chances': 65,
                'Related_trends': 'Digital Transformation, Gig Economy'
            }]
        }
    }

class KTrendOps(BaseModel):
    """Container for multiple trend operations."""
    trends: List[TrendOp] = Field(description="List of trend operations to analyze")

    model_config = {
        'json_schema_extra': {
            'examples': [{
                'trends': []  # Will be populated with TrendOp examples
            }]
        }
    }

class AnalysisInput(BaseModel):
    """Input model for analysis requests."""
    user_input: str = Field(description="User's business opportunity request")
    k: int = Field(default=10, ge=1, le=50, description="Number of trends to generate")
    generate_novel_ideas: bool = Field(default=True, description="Whether to generate novel ideas")

    model_config = {
        'json_schema_extra': {
            'examples': [{
                'user_input': 'Make San Francisco carbon neutral',
                'k': 5,
                'generate_novel_ideas': True
            }]
        }
    }

class StartupAnalysisResponse(BaseModel):
    """Model for the complete startup analysis response."""
    trends: List[TrendOp] = Field(description="List of analyzed trends and startup opportunities")

    model_config = {
        'json_schema_extra': {
            'examples': [{
                'trends': []  # Will be populated with TrendOp examples
            }]
        }
    }

class IntermediateStep(BaseModel):
    """Model for intermediate analysis steps."""
    step_name: str = Field(description="Name of the analysis step")
    output: str = Field(description="Raw output from the step")
    timestamp: str = Field(description="ISO format timestamp of when the step was completed")
    is_refined: bool = Field(default=False, description="Whether this step was refined due to quality check")
    refinement_count: int = Field(default=0, description="Number of times this step was refined")

class IntermediateResults(BaseModel):
    """Model for storing all intermediate results during analysis."""
    trend_analysis: Optional[IntermediateStep] = Field(default=None, description="Results from trend analysis step")
    opportunity_analysis: Optional[IntermediateStep] = Field(default=None, description="Results from opportunity analysis step")
    competitor_analysis: Optional[IntermediateStep] = Field(default=None, description="Results from competitor analysis step")
    final_result: Optional[StartupAnalysisResponse] = Field(default=None, description="Final parsed results")
    execution_time: float = Field(default=0.0, description="Total execution time in seconds")
    refinement_steps: List[IntermediateStep] = Field(default_factory=list, description="List of any refinement steps performed")

    model_config = {
        'json_schema_extra': {
            'examples': [{
                'trend_analysis': {
                    'step_name': 'trend_analysis',
                    'output': 'Trend analysis output...',
                    'timestamp': '2025-02-17T23:33:28Z',
                    'is_refined': False,
                    'refinement_count': 0
                },
                'opportunity_analysis': None,
                'competitor_analysis': None,
                'final_result': None,
                'execution_time': 0.0,
                'refinement_steps': []
            }]
        }
    }

class AnalysisOutput(BaseModel):
    """Model for API analysis response."""
    status: str = Field(description="Status of the analysis (success/error)")
    data: Dict[str, Any] = Field(description="Analysis results including all steps")
    error: Optional[str] = Field(default=None, description="Error message if any")

    model_config = {
        'json_schema_extra': {
            'examples': [{
                'status': 'success',
                'data': {
                    'trend_analysis': {'step_name': 'trend_analysis', 'output': '...'},
                    'opportunity_analysis': {'step_name': 'opportunity_analysis', 'output': '...'},
                    'competitor_analysis': {'step_name': 'competitor_analysis', 'output': '...'},
                    'final_result': {'trends': []},
                    'execution_time': 5.23,
                    'refinement_steps': []
                },
                'error': None
            }]
        }
    }

class FileUploadResponse(BaseModel):
    """Model for file upload response."""
    status: str = Field(description="Status of the upload (success/error)")
    file_id: Optional[str] = Field(default=None, description="ID of the uploaded file")
    error: Optional[str] = Field(default=None, description="Error message if any")

    model_config = {
        'json_schema_extra': {
            'examples': [{
                'status': 'success',
                'file_id': 'abc123',
                'error': None
            }]
        }
    }
