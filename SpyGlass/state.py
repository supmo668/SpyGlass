"""State management for the SpyGlass application."""
import reflex as rx
from typing import List, Dict, Any

class State(rx.State):
    """The app state."""
    
    # Query state
    query: str = ""
    is_processing: bool = False
    current_step: int = -1
    error_message: str = ""
    
    # Reports state
    public_reports: List[Dict[str, Any]] = []
    
    def set_query(self, query: str):
        """Update the query string."""
        self.query = query
    
    def start_processing(self):
        """Start the analysis process."""
        if not self.query:
            self.error_message = "Please enter a query first."
            return
            
        self.error_message = ""
        self.is_processing = True
        self.current_step = 0
        
        # Simulate some analysis steps
        self.public_reports = [
            {
                "title": "AI in Healthcare Report",
                "sections": ["Market Overview", "Key Players"],
                "is_public": True
            },
            {
                "title": "Technology Trends",
                "sections": ["Emerging Tech", "Future Outlook"],
                "is_public": False
            }
        ]
