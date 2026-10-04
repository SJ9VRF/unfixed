from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from math import exp
from interaction_engine.models import InteractionEvent, SignalType
from user_model.schema import ContextValue, PreferenceRecord, PreferenceSource, MemoryStability, UserState


@dataclass
class InferenceConfig:
    min_confidence: float = 0.50
    correction_bonus: float = 1.35
    recency_half_life_events: float = 10.0
    context_min_evidence: int = 2
    change_window: int = 4
    drift_threshold: float = 0.62


class PreferenceInferenceEngine:
    """Context-aware, recency-aware preference inference with lightweight change detection."""

    def __init__(self, config: InferenceConfig | None = None):
        self.config = config or InferenceConfig()

    def _event_weight(self, event: InteractionEvent, reverse_index: int) -> float:
        decay = 0.5 ** (reverse_index / max(self.config.recency_half_life_events, 1e-6))
        w = event.reliability * decay
        if event.signal_type == SignalType.CORRECTION:
            w *= self.config.correction_bonus
        return w

    def _aggregate(self, events: list[InteractionEvent]) -> tuple[dict[str, float], dict[str, int]]:
        scores: dict[str, float] = defaultdict(float)
        counts: dict[str, int] = defaultdict(int)
        total = len(events)
        for idx, e in enumerate(events):
            reverse_index = total - 1 - idx
            w = self._event_weight(e, reverse_index)
            scores[str(e.observed_value)] += w
            counts[str(e.observed_value)] += 1
        return scores, counts

    @staticmethod
    def _confidence(scores: dict[str, float], min_confidence: float) -> tuple[str, float, float]:
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_value, best = ranked[0]
        second = ranked[1][1] if len(ranked) > 1 else 0.0
        total = sum(scores.values())
        margin = (best - second) / max(total, 1e-9)
        evidence = 1 - exp(-total / 2.4)
        confidence = max(min_confidence, min(0.99, 0.43 + 0.34 * margin + 0.26 * evidence))
        return best_value, confidence, margin

    def _drift_score(self, events: list[InteractionEvent], current_value: str) -> float:
        if len(events) < self.config.change_window * 2:
            return 0.0
        old = events[:-self.config.change_window]
        recent = events[-self.config.change_window:]
        old_scores, _ = self._aggregate(old)
        recent_scores, _ = self._aggregate(recent)
        if not old_scores or not recent_scores:
            return 0.0
        old_value = max(old_scores.items(), key=lambda x: x[1])[0]
        recent_value = max(recent_scores.items(), key=lambda x: x[1])[0]
        if old_value == recent_value:
            return 0.0
        recent_total = sum(recent_scores.values())
        recent_support = recent_scores.get(recent_value, 0.0) / max(recent_total, 1e-9)
        correction_signal = any(e.signal_type == SignalType.CORRECTION for e in recent if str(e.observed_value) == recent_value)
        score = min(1.0, 0.55 * recent_support + (0.35 if correction_signal else 0.0) + 0.1)
        return score

    def infer(self, user_id: str, events: list[InteractionEvent]) -> UserState:
        grouped: dict[str, list[InteractionEvent]] = defaultdict(list)
        for e in events:
            if e.relevant and e.preference_key and e.observed_value is not None:
                grouped[e.preference_key].append(e)

        prefs: dict[str, PreferenceRecord] = {}
        now = datetime.now(timezone.utc)
        for key, key_events in grouped.items():
            scores, counts = self._aggregate(key_events)
            value, confidence, margin = self._confidence(scores, self.config.min_confidence)

            by_context: dict[str, list[InteractionEvent]] = defaultdict(list)
            for e in key_events:
                by_context[e.context].append(e)
            context_values: dict[str, ContextValue] = {}
            for ctx, ctx_events in by_context.items():
                if len(ctx_events) < self.config.context_min_evidence:
                    continue
                ctx_scores, ctx_counts = self._aggregate(ctx_events)
                ctx_value, ctx_conf, _ = self._confidence(ctx_scores, self.config.min_confidence)
                context_values[ctx] = ContextValue(
                    value=ctx_value,
                    confidence=ctx_conf,
                    evidence_count=sum(ctx_counts.values()),
                    last_updated_at=ctx_events[-1].timestamp,
                )

            source_types = {e.signal_type for e in key_events}
            src = PreferenceSource.EXPLICIT if (SignalType.EXPLICIT in source_types or SignalType.CORRECTION in source_types) else PreferenceSource.IMPLICIT
            drift = self._drift_score(key_events, value)
            uncertainty = None
            if drift >= self.config.drift_threshold:
                uncertainty = "recent evidence indicates preference drift"
                confidence = min(confidence, 0.78)
            elif margin <= 0.25:
                uncertainty = "competing evidence"

            prefs[key] = PreferenceRecord(
                key=key,
                value=value,
                confidence=confidence,
                source=src,
                evidence_count=sum(counts.values()),
                context=sorted(by_context),
                context_values=context_values,
                stability=MemoryStability.EVOLVING,
                last_confirmed_at=key_events[-1].timestamp if key_events else now,
                uncertainty_reason=uncertainty,
                drift_score=drift,
            )

        uncertainty = 1.0 if not prefs else 1 - sum(p.confidence for p in prefs.values()) / len(prefs)
        return UserState(user_id=user_id, preferences=prefs, global_uncertainty=max(0.0, min(1.0, uncertainty)))
