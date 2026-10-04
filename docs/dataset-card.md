# Dataset Card — The Unfixed User Synthetic Benchmark

## Purpose
Controlled evaluation of sparse, context-dependent and changing user preferences. It is a mechanism benchmark, not a demographic or population-representative user dataset.

## User state
Seven preference dimensions are sampled: answer detail, planning style, risk tolerance, travel priority, assistant autonomy, privacy sensitivity and preferred work time. Each preference can have a context-specific override with configurable probability.

## Interactions
Events include a preference key/value, signal type (explicit, implicit, correction), reliability, context, temporal ordering and relevance flag. Observation noise is higher for implicit signals than for explicit/corrective signals.

## Contexts
`general`, `work`, `travel`, `high_stakes`, `casual`.

## Splits
Reference controlled run: 220 training users and 90 held-out users. Seeds are fixed by the benchmark runner.

## Intended use
Algorithmic evaluation of inference, context conditioning, drift recovery, selection strategies and personalization gating.

## Not intended for
Claims about real human satisfaction, trust, demographic fairness, clinical behavior or population-level preference distributions.
