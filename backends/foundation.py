from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from backends.base import AgentBackend, AgentRequest, AgentResponse
from personalization.gate import PersonalizationGate
from user_model.schema import UserState

@dataclass
class CompletionAdapter:
    """Provider-agnostic completion adapter.

    Pass any callable `fn(prompt)->str` (hosted API, local model, test double). The
    research pipeline remains runnable without one; this class is an integration seam.
    """
    fn: Callable[[str], str]
    def complete(self,prompt:str)->str: return self.fn(prompt)

class GroundedFoundationBackend(AgentBackend):
    def __init__(self, adapter:CompletionAdapter, gate:PersonalizationGate):
        self.adapter=adapter; self.gate=gate

    def respond(self, request:AgentRequest, state:UserState)->AgentResponse:
        key=request.relevant_preference
        pref=state.preferences.get(key) if key else None
        gate_score=self.gate.score(request.prompt,key) if key else 0.0
        personalize=bool(pref and gate_score>=.5)
        grounding='No personal preference is relevant.'
        conf=1-gate_score; used=None
        if personalize:
            value,pconf=pref.value_for_context(request.context)
            grounding=(f'Relevant user preference: {key}={value}. '
                       f'Preference confidence={pconf:.2f}. Do not generalize beyond this context.')
            conf=min(gate_score,pconf); used=key
        system=("You are a calibrated personal assistant. Use only the supplied user-state evidence. "
                "Do not invent preferences. If evidence is weak or irrelevant, answer generically.\n")
        text=self.adapter.complete(system+grounding+'\nUser request: '+request.prompt)
        return AgentResponse(text,personalize,used,conf,
            f'gate={gate_score:.2f}; '+('grounded preference supplied' if personalize else 'personalization withheld'))
