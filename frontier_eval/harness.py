from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Iterable
import json
import statistics


@dataclass(frozen=True)
class EvalTask:
    task_id: str
    family: str
    prompt: str
    initial_state: dict[str, Any]
    expected: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GraderResult:
    name: str
    score: float
    passed: bool
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class TrialResult:
    task_id: str
    trial_index: int
    output: dict[str, Any]
    final_state: dict[str, Any]
    trajectory: list[dict[str, Any]]
    graders: list[GraderResult]
    latency_ms: float | None = None
    cost_usd: float | None = None

    @property
    def score(self) -> float:
        return sum(g.score for g in self.graders) / max(len(self.graders), 1)

    @property
    def passed(self) -> bool:
        return all(g.passed for g in self.graders)


@dataclass
class EvalReport:
    trials: list[TrialResult]

    def summary(self) -> dict[str, Any]:
        scores = [t.score for t in self.trials]
        latencies = [t.latency_ms for t in self.trials if t.latency_ms is not None]
        costs = [t.cost_usd for t in self.trials if t.cost_usd is not None]
        by_family: dict[str, list[TrialResult]] = {}
        for trial in self.trials:
            family = trial.output.get("family", "unknown")
            by_family.setdefault(family, []).append(trial)
        return {
            "n_trials": len(self.trials),
            "pass_rate": sum(t.passed for t in self.trials) / max(len(self.trials), 1),
            "mean_score": statistics.fmean(scores) if scores else 0.0,
            "median_latency_ms": statistics.median(latencies) if latencies else None,
            "total_cost_usd": sum(costs) if costs else None,
            "families": {
                family: {
                    "n": len(items),
                    "pass_rate": sum(t.passed for t in items) / len(items),
                    "mean_score": statistics.fmean(t.score for t in items),
                }
                for family, items in sorted(by_family.items())
            },
        }

    def to_json(self, path: str) -> None:
        payload = {
            "summary": self.summary(),
            "trials": [
                {
                    **asdict(t),
                    "score": t.score,
                    "passed": t.passed,
                }
                for t in self.trials
            ],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, sort_keys=True)


AgentFn = Callable[[EvalTask, int], tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], float | None, float | None]]
GraderFn = Callable[[EvalTask, dict[str, Any], dict[str, Any], list[dict[str, Any]]], GraderResult]


class EvalHarness:
    """Small, deterministic eval harness with task/trial/grader/trajectory semantics.

    The harness grades outcomes and state separately from execution paths. This keeps
    valid alternative behaviors from being rejected simply for taking a different
    route, while still preserving complete trajectories for debugging.
    """

    def __init__(self, agent: AgentFn, graders: Iterable[GraderFn], trials_per_task: int = 3):
        if trials_per_task < 1:
            raise ValueError("trials_per_task must be >= 1")
        self.agent = agent
        self.graders = list(graders)
        if not self.graders:
            raise ValueError("at least one grader is required")
        self.trials_per_task = trials_per_task

    def run(self, tasks: Iterable[EvalTask]) -> EvalReport:
        results: list[TrialResult] = []
        for task in tasks:
            for trial_idx in range(self.trials_per_task):
                output, final_state, trajectory, latency_ms, cost_usd = self.agent(task, trial_idx)
                output = dict(output)
                output.setdefault("family", task.family)
                grader_results = [
                    grader(task, output, final_state, trajectory) for grader in self.graders
                ]
                results.append(
                    TrialResult(
                        task_id=task.task_id,
                        trial_index=trial_idx,
                        output=output,
                        final_state=final_state,
                        trajectory=trajectory,
                        graders=grader_results,
                        latency_ms=latency_ms,
                        cost_usd=cost_usd,
                    )
                )
        return EvalReport(results)
