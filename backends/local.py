from __future__ import annotations
from backends.base import AgentBackend, AgentRequest, AgentResponse
from personalization.gate import PersonalizationGate
from user_model.schema import UserState

class LocalPersonalAgentBackend(AgentBackend):
    """Offline reference backend. It exposes the same contract a hosted FM adapter would use."""
    def __init__(self, gate: PersonalizationGate|None=None): self.gate=gate

    def respond(self, request: AgentRequest, state: UserState) -> AgentResponse:
        key=request.relevant_preference
        pref=state.preferences.get(key) if key else None
        score=self.gate.score(request.prompt,key) if self.gate else (0.9 if key else 0.05)
        personalize=bool(pref and score>=.5)
        if personalize:
            value,conf=pref.value_for_context(request.context)
            text=f"Recommendation adapted to {key}={value}."
            rationale=f"Relevant preference {key}; gate={score:.2f}; preference confidence={conf:.2f}."
            return AgentResponse(text,True,key,min(conf,score),rationale)
        return AgentResponse("Answer without using personal preferences.",False,None,1-score,f"Personalization gate={score:.2f}; no relevant preference applied.")
