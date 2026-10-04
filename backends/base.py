from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from user_model.schema import UserState

@dataclass
class AgentRequest:
    prompt: str
    context: str='general'
    relevant_preference: str|None=None

@dataclass
class AgentResponse:
    text: str
    personalized: bool
    preference_used: str|None
    confidence: float
    rationale: str

class AgentBackend(ABC):
    @abstractmethod
    def respond(self, request: AgentRequest, state: UserState) -> AgentResponse: ...
