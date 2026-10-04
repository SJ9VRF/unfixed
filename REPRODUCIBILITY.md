# Reproducibility

The repository has two deliberately different verification paths.

## 1. Research verification

Run this on a working checkout after installing the development and paper dependencies:

```bash
pip install -e '.[dev,paper]'
make verify
```

`make verify` runs the full test/coverage gate, red-team checks, paper and reference claim verification, the seed-level statistical audit, the frontier-style smoke evaluation, and the model-change regression gate. It then rebuilds `MANIFEST.json` *after* all checks that may write result files.

This command verifies the current frozen evidence. It does **not** silently regenerate the long-running benchmark outputs; benchmark regeneration is a separate operation:

```bash
make benchmark
```

Keeping regeneration separate prevents a verification command from changing the evidence it is supposed to audit.

## 2. Release verification

After extracting a release archive, run:

```bash
python scripts/verify_release.py
```

This check is read-only. It verifies every manifest hash and byte count, paper presence and author metadata, absence of cache/build junk, absence of project/build dates in PDF metadata, and absence of old public branding/name variants.

## Paper-facing reproduction

```bash
make paper
python scripts/verify_paper_claims.py
```

The paper-facing runner regenerates the controlled experiments, figures, and claim checks used in the manuscript. Some experiments are intentionally slower than the release verifier.

## Evidence boundary

The controlled benchmark uses synthetic training-user ground truth as supervision. Held-out test users are disjoint, and test-time inference does not read simulator-only ground-truth metadata. The repository contains regression tests for that invariant. External-model, public-benchmark, and real-user results are not inferred from the simulator and are not claimed until run independently.
