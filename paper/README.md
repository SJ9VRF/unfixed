# Research manuscript

## Manuscript

- `the_unfixed_user.tex` - self-contained manuscript source used for the reproducible PDF in this release.
- `the_unfixed_user.pdf` - compiled research manuscript.
- `submission_readiness.md` - notes for converting the research manuscript into a conference submission using the official venue template.

The manuscript is intentionally conservative about unexecuted evidence. External personalization benchmarks, recruited human judgments, and foundation-model post-training remain gated until the corresponding data/model resources are available.

## Reproduce paper experiments

```bash
python -m evals.suite.paper_runner
python scripts/build_paper_figures.py
python scripts/verify_paper_claims.py
```

The full paper suite is CPU-heavy because it includes repeated-seed augmentation studies and a trained PyTorch response-level baseline. Individual outputs can also be regenerated with the functions in `evals/suite/paper_runner.py` and `evals/response_level/benchmark.py`.

## Conference formatting

The release PDF is a stable research-manuscript render. It is not formatted as an official conference submission. Before submission, compile the same manuscript content with the official NeurIPS style package supplied by the conference and rerun the page-limit/checklist checks. The research release keeps the style dependency separate so a third-party conference file is not silently copied or modified.

## Reproducing the five-seed response-level result

```bash
make paper-response
```

This trains a fresh structured learner, relevance gate, and scratch PyTorch ranker for each of five independent seeds and rewrites the per-seed and aggregate CSV/JSON files before re-verifying paper claims.

## Public and anonymous manuscript builds

- `the_unfixed_user.pdf`: public research manuscript with Aura Yavary as author.
- `the_unfixed_user_anonymous.pdf`: identity-redacted manuscript for double-blind review preparation.

The anonymous version is still a stable research-manuscript render. A conference submission must be recompiled with the official NeurIPS style for the submission year and include the official checklist in the required single-PDF ordering.
