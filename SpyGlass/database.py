from sqlmodel import SQLModel, Field
from typing import List, Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BIReport(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    sections: List[str] = Field(sa_column=Column(JSON))  # Store as JSON
    charts: List[str] = Field(sa_column=Column(JSON))    # Chart URLs
    is_public: bool = False
    owner_id: str = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ApertureDB configuration
from aperture_sdk.client import ApertureClient
aperture = ApertureClient(
    api_key="your-aperture-key",
    storage_bucket="spyglass-reports"
)

def get_engine():
    return create_engine("sqlite:///spyglass.db")
