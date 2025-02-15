import reflex as rx
import os
from dotenv import load_dotenv
from stytch import Client
from aperture_sdk import ApertureClient

# Load environment variables
load_dotenv()

class State(rx.State):
    """Application state management"""
    search_query: str = ""
    current_step: int = 0
    processing_steps: list = ["Ideation", "Ranking", "Matching", "Analysis", "Reporting"]
    public_reports: list[dict] = []
    user_session: dict = {}
    
    # Initialize clients
    aperture = ApertureClient(api_key=os.getenv("APERTUREDB_API_KEY"))
    stytch = Client(
        project_id=os.getenv("STYTCH_PROJECT_ID"),
        secret=os.getenv("STYTCH_SECRET"),
        environment="test"
    )
    
    def load_public_reports(self):
        """Load public reports from ApertureDB"""
        try:
            self.public_reports = self.aperture.query("BIReport").filter(public=True).limit(10)
        except Exception as e:
            print(f"Error loading public reports: {e}")
            self.public_reports = []
    
    async def process_query(self):
        """Main processing workflow"""
        try:
            for step in range(len(self.processing_steps)):
                self.current_step = step
                await self.sleep(1)  # Simulate processing
            
            # Store final report
            report = {
                "sections": [self.search_query + " analysis"],
                "images": [],
                "public": True
            }
            self.aperture.store("BIReport", report)
            self.load_public_reports()
        except Exception as e:
            print(f"Error processing query: {e}")
            self.current_step = 0
