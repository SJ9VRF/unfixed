from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field

class SignalType(str, Enum):
    EXPLICIT = 'explicit'
    IMPLICIT = 'implicit'
    CORRECTION = 'correction'

class InteractionEvent(BaseModel):
    event_id: str
    user_id: str
    preference_key: str | None = None
    observed_value: str | None = None
    signal_type: SignalType = SignalType.IMPLICIT
    reliability: float = Field(default=0.6, ge=0.0, le=1.0)
    context: str = 'general'
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    relevant: bool = True
    metadata: dict = Field(default_factory=dict)
