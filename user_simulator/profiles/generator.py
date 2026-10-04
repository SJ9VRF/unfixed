from __future__ import annotations
import random
from dataclasses import dataclass
from typing import Any
from user_model.schema import ContextValue, MemoryStability, PreferenceRecord, PreferenceSource, UserState

PREFERENCE_SPACE: dict[str, list[Any]] = {
    "answer_detail": ["concise", "balanced", "detailed"],
    "planning_style": ["spontaneous", "structured"],
    "risk_tolerance": ["low", "medium", "high"],
    "travel_priority": ["price", "convenience", "comfort"],
    "autonomy": ["ask_first", "suggest_first", "act_when_reversible"],
    "privacy_sensitivity": ["low", "medium", "high"],
    "work_time": ["morning", "afternoon", "evening"],
}

@dataclass
class SyntheticProfileConfig:
    n_preferences: int = 5
    seed: int | None = None
    context_dependence_rate: float = 0.30


def generate_user_state(user_id: str, config: SyntheticProfileConfig | None = None) -> UserState:
    config = config or SyntheticProfileConfig()
    rng = random.Random(config.seed)
    keys = rng.sample(list(PREFERENCE_SPACE), k=min(config.n_preferences, len(PREFERENCE_SPACE)))
    prefs = {}
    for key in keys:
        base=rng.choice(PREFERENCE_SPACE[key])
        ctx_values={}
        if rng.random() < config.context_dependence_rate and len(PREFERENCE_SPACE[key])>1:
            ctx=rng.choice(['work','travel','high_stakes','casual'])
            alt=rng.choice([v for v in PREFERENCE_SPACE[key] if v != base])
            ctx_values[ctx]=ContextValue(value=alt,confidence=rng.uniform(.78,.96),evidence_count=rng.randint(2,6))
        prefs[key] = PreferenceRecord(
            key=key, value=base, confidence=rng.uniform(0.75, 0.98),
            source=PreferenceSource.EXPLICIT, evidence_count=rng.randint(2, 8),
            context=sorted(ctx_values), context_values=ctx_values,
            stability=MemoryStability.STABLE if rng.random() > 0.35 else MemoryStability.EVOLVING,
        )
    return UserState(
        user_id=user_id, preferences=prefs,
        communication_style={"tone": rng.choice(["direct", "warm", "neutral"])},
        global_uncertainty=0.1,
    )
