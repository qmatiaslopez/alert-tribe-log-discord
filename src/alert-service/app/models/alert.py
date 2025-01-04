from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class EventType(str, Enum):
    """Types of game events that can trigger alerts"""
    STRUCTURE_DESTROYED = "STRUCTURE_DESTROYED"
    MEMBER_KILLED = "MEMBER_KILLED"
    CREATURE_KILLED = "CREATURE_KILLED"

class Alert(BaseModel):
    """Model for game alerts"""
    event_type: EventType
    timestamp: datetime
    map: str = Field(..., description="Game map where the event occurred")
    victim: str = Field(..., description="The destroyed structure/killed member/creature")
    perpetrator: str = Field(..., description="Who caused the event")
    perpetrator_tribe: str = Field(..., description="Tribe of the perpetrator")