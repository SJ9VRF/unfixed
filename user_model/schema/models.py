from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, Field


class PreferenceSource(str, Enum):
    EXPLICIT = "explicit"
    IMPLICIT = "implicit"
    INFERRED = "inferred"
    SYNTHETIC = "synthetic"


class MemoryStability(str, Enum):
    TEMPORARY = "temporary"
    EVOLVING = "evolving"
    STABLE = "stable"


class ContextValue(BaseModel):
    value: Any
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_count: int = Field(default=1, ge=0)
    last_updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PreferenceRecord(BaseModel):
    key: str
    value: Any
    confidence: float = Field(ge=0.0, le=1.0)
    source: PreferenceSource
    evidence_count: int = Field(default=1, ge=0)
    context: list[str] = Field(default_factory=list)
    context_values: dict[str, ContextValue] = Field(default_factory=dict)
    stability: MemoryStability = MemoryStability.EVOLVING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_confirmed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    active: bool = True
    conflicts_with: list[str] = Field(default_factory=list)
    uncertainty_reason: str | None = None
    drift_score: float = Field(default=0.0, ge=0.0, le=1.0)

    def value_for_context(self, context: str | None) -> tuple[Any, float]:
        if context and context in self.context_values:
            c = self.context_values[context]
            return c.value, c.confidence
        return self.value, self.confidence


class GoalRecord(BaseModel):
    key: str
    description: str
    priority: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    status: Literal["active", "paused", "completed", "abandoned"] = "active"
    context: list[str] = Field(default_factory=list)


class UserState(BaseModel):
    user_id: str
    preferences: dict[str, PreferenceRecord] = Field(default_factory=dict)
    goals: dict[str, GoalRecord] = Field(default_factory=dict)
    constraints: list[str] = Field(default_factory=list)
    communication_style: dict[str, Any] = Field(default_factory=dict)
    temporal_state: dict[str, Any] = Field(default_factory=dict)
    global_uncertainty: float = Field(default=1.0, ge=0.0, le=1.0)

    def active_preference(self, key: str) -> PreferenceRecord | None:
        pref = self.preferences.get(key)
        return pref if pref and pref.active else None
