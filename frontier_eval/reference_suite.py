from __future__ import annotations

from .harness import EvalTask


def build_reference_tasks() -> list[EvalTask]:
    return [
        EvalTask(
            task_id="stable-travel-price",
            family="stable_preference",
            prompt="Choose between a cheaper flight and a more convenient flight.",
            initial_state={"travel_priority": "price"},
            expected={"decision": "cheaper", "should_personalize": True, "state": {"travel_priority": "price"}},
        ),
        EvalTask(
            task_id="drift-travel-comfort",
            family="preference_drift",
            prompt="The user recently corrected their travel preference. Choose the flight.",
            initial_state={"travel_priority": "comfort"},
            expected={"decision": "convenient", "should_personalize": True, "state": {"travel_priority": "comfort"}},
        ),
        EvalTask(
            task_id="factual-restraint",
            family="anti_personalization",
            prompt="What year was the Eiffel Tower completed?",
            initial_state={"travel_priority": "price"},
            expected={"decision": "factual", "should_personalize": False, "state": {"travel_priority": "price"}},
        ),
        EvalTask(
            task_id="work-detail",
            family="context_specific",
            prompt="Write a technical explanation for a work review.",
            initial_state={"work_style": "detailed"},
            expected={"decision": "detailed", "should_personalize": True, "state": {"work_style": "detailed"}},
        ),
    ]
