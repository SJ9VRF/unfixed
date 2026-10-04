# Scaling and systems design

The reference implementation is intentionally small enough to reproduce on a laptop, but the architecture is designed so the expensive parts can scale independently.

## What scales with users

The user-state path is partitionable by user identifier. Interaction ingestion, state updates, conflict resolution, and retrieval can therefore be sharded without cross-user synchronization. The important invariant is that one user's evidence cannot enter another user's state or training examples.

## What scales with experiments

Evaluation is embarrassingly parallel across task × trial × model. The harness stores each trial independently and aggregates only after grading. At larger scale, execution can move from local processes to a job queue without changing the task or grader contracts.

Synthetic generation is also parallel across users and candidate scenarios. Verification and selection remain separate stages so expensive model-based verification can be cached while selection policies are changed cheaply.

## Expensive model path

A production experiment would separate:

1. trajectory generation;
2. verifier / reward-model inference;
3. data filtering and deduplication;
4. post-training;
5. frozen evaluation;
6. regression triage.

The repository keeps these interfaces distinct because coupling generation directly to training makes it difficult to attribute regressions.

## Failure containment

- Every trial starts from explicit task state rather than shared mutable state.
- User-state provenance is retained so corrections can supersede inferred preferences.
- Consequential actions sit behind an authorization boundary above personalization.
- Model changes must pass behavior-level regression thresholds before headline results are updated.
- External-model adapters cannot change benchmark labels or grader criteria.

## Observability

A scaled version should log run configuration, model identifier, data version, task identifier, grader versions, token/cost telemetry, latency, and failure category. The included experiment registry already captures the core run metadata; distributed infrastructure would extend rather than replace that contract.

## Cost model

The offline benchmark has no hosted-model charge. For external models, cost should be reported per task and per successful task, not as a single aggregate API bill. This makes regressions visible when a stronger model improves quality by using disproportionately more tokens or retries.
