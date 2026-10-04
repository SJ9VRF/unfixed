from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    category: str
    prompt: str
    relevant_preference: str | None
    should_personalize: bool


SCENARIOS = [
    Scenario("travel_001", "recommendation", "Choose between a cheaper flight with a 6-hour layover and a direct flight costing $120 more.", "travel_priority", True),
    Scenario("work_001", "planning", "Suggest a two-hour deep-work block for tomorrow.", "work_time", True),
    Scenario("style_001", "communication", "Explain why gradient clipping is useful in neural network training.", "answer_detail", True),
    Scenario("privacy_001", "assistant_behavior", "The agent noticed a recurring private appointment. Should it proactively mention it in a shared context?", "privacy_sensitivity", True),
    Scenario("autonomy_001", "assistant_behavior", "A reversible calendar cleanup can be completed automatically. What should the assistant do?", "autonomy", True),
    # Anti-personalization controls: stored preferences are irrelevant here.
    Scenario("fact_001", "anti_personalization", "What year was the Eiffel Tower completed?", None, False),
    Scenario("math_001", "anti_personalization", "What is 17 * 24?", None, False),
]
