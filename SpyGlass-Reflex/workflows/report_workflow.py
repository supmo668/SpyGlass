"""Workflow for report generation and management."""
from typing import Dict, Any, List
from ..api.report_api import ReportAPI
from ..models.report import Report

class ReportWorkflow:
    """Handles the business logic for report operations."""
    
    def __init__(self):
        self.api = ReportAPI()
    
    async def generate_report(self, data: Dict[str, Any]) -> Report:
        """Generate a new report."""
        return await self.api.create_report(data)
    
    async def get_user_reports(self, user_id: str) -> List[Report]:
        """Get all reports for a user."""
        return await self.api.get_user_reports(user_id)
    
    async def get_report_details(self, report_id: str) -> Report:
        """Get detailed information about a specific report."""
        return await self.api.get_report(report_id)
