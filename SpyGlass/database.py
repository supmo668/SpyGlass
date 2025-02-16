from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class User(BaseModel):
    """User model for authentication."""
    id: str
    created_at: datetime = datetime.utcnow()

class BIReport(BaseModel):
    """Business Intelligence Report model."""
    id: Optional[str] = None
    title: str
    sections: List[str]
    charts: List[str] = []
    is_public: bool = False
    owner_id: Optional[str] = None
    created_at: datetime = datetime.utcnow()

    def to_aperture_entity(self) -> dict:
        """Convert to ApertureDB entity format."""
        return {
            "_id": self.id if self.id else None,
            "class": "BIReport",
            "title": self.title,
            "sections": self.sections,
            "charts": self.charts,
            "is_public": self.is_public,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_aperture_entity(cls, entity: dict) -> "BIReport":
        """Create from ApertureDB entity."""
        return cls(
            id=entity.get("_id"),
            title=entity.get("title", "Untitled Report"),
            sections=entity.get("sections", []),
            charts=entity.get("charts", []),
            is_public=entity.get("is_public", False),
            owner_id=entity.get("owner_id"),
            created_at=datetime.fromisoformat(entity.get("created_at")) if entity.get("created_at") else datetime.utcnow()
        )
