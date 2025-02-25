"""API client for report-related operations."""
from typing import Dict, Any, List
import httpx
from ..models.report import Report

class ReportAPI:
    """Client for interacting with the report API."""
    
    def __init__(self):
        self.base_url = "http://api.spyglass.local"  # Configure in environment
        self.client = httpx.AsyncClient()
    
    async def create_report(self, data: Dict[str, Any]) -> Report:
        """Create a new report."""
        response = await self.client.post(f"{self.base_url}/reports", json=data)
        response.raise_for_status()
        return Report(**response.json())
    
    async def get_user_reports(self, user_id: str) -> List[Report]:
        """Get all reports for a user."""
        response = await self.client.get(f"{self.base_url}/users/{user_id}/reports")
        response.raise_for_status()
        return [Report(**report) for report in response.json()]
    
    async def get_report(self, report_id: str) -> Report:
        """Get a specific report."""
        response = await self.client.get(f"{self.base_url}/reports/{report_id}")
        response.raise_for_status()
        return Report(**response.json())
