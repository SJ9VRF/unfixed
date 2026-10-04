# Human Evaluation Protocol

## Goal
Measure whether personalization is useful, correctly scoped, calibrated, and robust to changing preferences. This protocol is intentionally separate from the synthetic benchmark; no human-study claim is made until real annotations are collected.

## Design
- Blind pairwise comparison: **personalized** vs **non-personalized/retrieval baseline**.
- Randomized left/right response order.
- At least 3 independent raters per item for research-grade reporting.
- Stratify scenarios by cold-start, stable preference, context-dependent preference, preference reversal, ambiguous evidence, conflict, and anti-personalization.
- Keep factual content constant where possible so the comparison isolates personalization quality.

## Rating dimensions (1-5)
1. User understanding
2. Usefulness
3. Appropriate degree of personalization
4. Factual correctness
5. Trustworthiness

Binary flags:
- over-personalized
- relied on stale preference
- invented a preference
- should have asked instead of acting
- personalization was irrelevant

## Primary endpoints
- Pairwise win rate with 95% bootstrap CI
- Appropriate-personalization mean score
- Over-personalization rate
- Stale-preference error rate
- Inter-rater agreement (Krippendorff-style nominal agreement proxy in included tooling)

## Exclusion criteria
- Corrupted or incomplete annotations
- Item shown to same rater twice
- Rater completion time below a configurable floor if the study platform exposes timing

## Reporting rules
- Report participant count, item count, raters/item, recruitment source, date window, and exact inclusion/exclusion rules.
- Never pool synthetic-user metrics with human preference ratings.
- Predeclare primary endpoint before collecting labels.
- Include negative/null results.

## Power planning
A lightweight normal-approximation power analysis is included in `human_eval/power.py` and `human_eval/power_analysis.json`. With two-sided alpha 0.05 and target power 0.80, the independent-judgment approximation requires roughly 543 judgments for a 56% pairwise win rate, 305 for 58%, 194 for 60%, 134 for 62%, and 85 for 65%. These are judgment counts, not participant counts. A repeated-measures study must inflate for within-participant clustering and report participant-level uncertainty.
