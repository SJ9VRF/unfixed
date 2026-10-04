from __future__ import annotations

import argparse
from pathlib import Path

from evals.suite.runner import run_full_benchmark
from evals.suite.v2_runner import run_v2_benchmark
from evals.suite.v3_runner import repeated_seed_stability, downstream_synthetic_utility, noise_stress
from evals.suite.paper_runner import (
    oracle_vs_pseudo, synthetic_mass_sweep, mass_aware_mitigation,
    drift_baselines, selective_risk, personalization_regret,
)
from evals.response_level.repeated import run_repeated_response_level


def run(exp_id: str, out_dir: str | Path):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    exp = exp_id.upper()
    if exp == 'EXP-001':
        return run_full_benchmark(out)
    if exp in {'EXP-002','EXP-004'}:
        return run_v2_benchmark(out)
    if exp == 'EXP-003':
        return repeated_seed_stability(out)
    if exp == 'EXP-005':
        return downstream_synthetic_utility(out)
    if exp == 'EXP-006':
        return oracle_vs_pseudo(out)
    if exp == 'EXP-007':
        return synthetic_mass_sweep(out)
    if exp == 'EXP-008':
        return mass_aware_mitigation(out)
    if exp == 'EXP-009':
        return drift_baselines(out)
    if exp == 'EXP-010':
        return noise_stress(out)
    if exp == 'EXP-011':
        return selective_risk(out)
    if exp == 'EXP-012':
        return run_repeated_response_level(out)
    if exp == 'EXP-013':
        return personalization_regret(out)
    raise SystemExit(f'Unknown experiment id: {exp_id}')


def main():
    p = argparse.ArgumentParser(description='Re-run one canonical experiment from the Evidence Layer.')
    p.add_argument('experiment', help='EXP-001 ... EXP-013')
    p.add_argument('--out', default='scratch/reproduced', help='Output directory; defaults to scratch/reproduced')
    args = p.parse_args()
    run(args.experiment, args.out)
    print(f'{args.experiment.upper()} complete -> {args.out}')


if __name__ == '__main__':
    main()
