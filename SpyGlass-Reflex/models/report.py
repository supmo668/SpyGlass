"""Report data models."""
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional

class Report(BaseModel):
    """Report model."""
    id: str
    title: str
    description: str
    created_at: datetime
    user_id: str
    data: Dict[str, Any]
    status: str
    metadata: Optional[Dict[str, Any]] = None
