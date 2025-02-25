"""State management for the SpyGlass application."""
from typing import List, Dict, Any
import reflex as rx
from reflex.vars import Var

class State(rx.State):
    """The app state."""
    
    # Authentication state
    is_authenticated: bool = False
    current_user: Dict[str, Any] = {}
    
    # Query state
    query: str = ""
    is_processing: bool = False
    current_page: int = 1
    items_per_page: int = 8  # 2 rows x 4 columns
    
    # Reports state
    _reports: List[Dict] = [
        {"title": f"Report {i}", "image_url": f"https://picsum.photos/400?random={i}"} 
        for i in range(1, 17)  # 16 sample reports
    ]
    current_report: Dict[str, Any] = {}
    
    # UI state
    is_loading: bool = False
    error_message: str = ""
    
    @rx.var
    def reports(self) -> List[Dict]:
        """Get the paginated list of reports."""
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        return self._reports[start_idx:end_idx]
    
    @rx.var
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        return len(self._reports) // self.items_per_page + (1 if len(self._reports) % self.items_per_page > 0 else 0)

    @rx.var
    def visible_page_numbers(self) -> List[int]:
        """Get list of visible page numbers."""
        return list(range(
            max(2, self.current_page - 1),
            min(self.total_pages, self.current_page + 2) + 1
        ))
    
    @rx.var
    def is_first_page(self) -> bool:
        """Check if on first page."""
        return self.current_page <= 1
    
    @rx.var
    def is_last_page(self) -> bool:
        """Check if on last page."""
        return self.current_page >= self.total_pages

    def set_query(self, query: str):
        """Update the query string."""
        self.query = query
    
    def next_page(self):
        """Go to next page."""
        if not self.is_last_page:
            self.current_page += 1
    
    def prev_page(self):
        """Go to previous page."""
        if not self.is_first_page:
            self.current_page -= 1
    
    def set_page(self, page: int):
        """Set specific page."""
        if 1 <= page <= self.total_pages:
            self.current_page = page
            
    async def process_query(self):
        """Process the current query."""
        self.is_processing = True
        try:
            # Process query logic here
            pass
        finally:
            self.is_processing = False
