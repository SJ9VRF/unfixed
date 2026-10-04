# Unexpected Findings

## More synthetic evidence was not monotonically better

The starting expectation was that verified, targeted synthetic interactions would reduce the amount of real user evidence needed. Instead, several forms of augmentation hurt downstream accuracy. The reversal persisted under oracle labels.

The useful question became **not “is this synthetic example plausible?” but “what does adding this correlated evidence do to the effective training distribution?”**

## Oracle-correct examples can still be harmful

The project initially treated label correctness as the likely bottleneck. The oracle diagnostic falsified that explanation in the controlled setting. This was the turning point from a verifier-centric project to a dataset-composition study.

## The “smart” selector was not the useful selector

Boundary/failure/information proxies changed which examples were selected, but high proxy value did not reliably predict downstream gain. This is why selector scores are reported as diagnostics, not success metrics.

## A standard detector beat the custom drift heuristic

The custom drift score looked strong in isolation (ROC-AUC 0.928). It stopped looking like a contribution when EWMA/CUSUM reached ~0.98. The method stayed in the codebase; the novelty claim was removed.

## The neural ranker was worse than simple structured policies

A scratch PyTorch response ranker did not rescue the task. It averaged 0.450 ± 0.022 across five seeds versus 0.680 ± 0.013 for Bayesian state + restraint. The negative result is kept because it rules out “just add a neural layer” as an explanation for the behavior gains.

## Dense history changes which baseline is strongest

The learned real-only model dominates retrieval in the sparse regime, but by 20–50 interactions retrieval becomes competitive or slightly stronger on the controlled cold-start benchmark. The project therefore avoids claiming universal superiority over retrieval.
