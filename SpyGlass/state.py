"""State management for the SpyGlass application."""
from typing import List, Dict
import reflex as rx

class State(rx.State):
    """The app state."""
    
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
    
    @rx.var
    def reports(self) -> List[Dict]:
        """Get the paginated list of reports."""
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        return self._reports[start_idx:end_idx]
    
    @rx.var
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        return (len(self._reports) + self.items_per_page - 1) // self.items_per_page
    
    def set_query(self, query: str):
        """Update the query string."""
        self.query = query
    
    def next_page(self):
        """Go to next page."""
        if self.current_page < self.total_pages:
            self.current_page += 1
    
    def prev_page(self):
        """Go to previous page."""
        if self.current_page > 1:
            self.current_page -= 1
    
    def set_page(self, page: int):
        """Set specific page."""
        if 1 <= page <= self.total_pages:
            self.current_page = page
    
    async def process_query(self):
        """Process the query and redirect to demo page."""
        if not self.query.strip():  # Don't process empty queries
            return
            
        self.is_processing = True
        # Simulate processing delay
        yield rx.set_timeout(3, self.finish_processing)
    
    def finish_processing(self):
        """Finish processing and redirect."""
        self.is_processing = False
        return rx.redirect("/demo")
