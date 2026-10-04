from __future__ import annotations

from typing import Any
from .harness import EvalTask, GraderResult


def outcome_match(task: EvalTask, output: dict[str, Any], final_state: dict[str, Any], trajectory: list[dict[str, Any]]) -> GraderResult:
    target = task.expected.get("decision")
    observed = output.get("decision")
    passed = target == observed
    return GraderResult("outcome_match", 1.0 if passed else 0.0, passed, {"expected": target, "observed": observed})


def restraint(task: EvalTask, output: dict[str, Any], final_state: dict[str, Any], trajectory: list[dict[str, Any]]) -> GraderResult:
    should_personalize = bool(task.expected.get("should_personalize", True))
    personalized = bool(output.get("personalized", False))
    passed = personalized == should_personalize
    return GraderResult("restraint", 1.0 if passed else 0.0, passed, {"should_personalize": should_personalize, "personalized": personalized})


def state_verification(task: EvalTask, output: dict[str, Any], final_state: dict[str, Any], trajectory: list[dict[str, Any]]) -> GraderResult:
    expected_state = task.expected.get("state", {})
    mismatches = {k: {"expected": v, "observed": final_state.get(k)} for k, v in expected_state.items() if final_state.get(k) != v}
    passed = not mismatches
    score = 1.0 if passed else max(0.0, 1.0 - len(mismatches) / max(len(expected_state), 1))
    return GraderResult("state_verification", score, passed, {"mismatches": mismatches})


def trajectory_sanity(task: EvalTask, output: dict[str, Any], final_state: dict[str, Any], trajectory: list[dict[str, Any]]) -> GraderResult:
    # We do not prescribe a specific path; this grader only enforces inspectability.
    passed = bool(trajectory) and all("event" in step for step in trajectory)
    return GraderResult("trajectory_sanity", 1.0 if passed else 0.0, passed, {"steps": len(trajectory)})
