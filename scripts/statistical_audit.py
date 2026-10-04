#!/usr/bin/env python3
"""Seed-level statistical audit for headline repeated-run comparisons.

Uses only the Python standard library. The purpose is not to manufacture
significance from a small number of seeds, but to expose paired deltas,
consistency, exact sign-test probabilities, and standardized effects.
"""
from __future__ import annotations
import csv, json, math, statistics
from pathlib import Path
from math import comb

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'
DOCS = ROOT / 'docs'


def exact_sign_test_two_sided(wins: int, losses: int) -> float:
    n = wins + losses
    if n == 0:
        return 1.0
    k = min(wins, losses)
    tail = sum(comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def paired_summary(deltas: list[float]) -> dict:
    nonzero = [d for d in deltas if d != 0]
    wins = sum(d > 0 for d in nonzero)
    losses = sum(d < 0 for d in nonzero)
    mean = statistics.mean(deltas)
    sd = statistics.stdev(deltas) if len(deltas) > 1 else 0.0
    dz = mean / sd if sd else None
    return {
        'n_pairs': len(deltas),
        'mean_delta': mean,
        'sd_delta': sd,
        'min_delta': min(deltas),
        'max_delta': max(deltas),
        'wins': wins,
        'losses': losses,
        'ties': len(deltas) - len(nonzero),
        'exact_sign_test_two_sided_p': exact_sign_test_two_sided(wins, losses),
        'paired_standardized_effect_dz': dz,
    }


def load_mass() -> dict:
    rows = list(csv.DictReader((RESULTS / 'paper_mass_control_seeds.csv').open()))
    def delta(a, b):
        return [float(r[a]) - float(r[b]) for r in rows]
    return {
        'raw_vs_real_only': paired_summary(delta('uces_raw', 'real_only')),
        'mass_capped_vs_raw': paired_summary(delta('mass_capped_uces', 'uces_raw')),
        'mass_capped_vs_real_only': paired_summary(delta('mass_capped_uces', 'real_only')),
    }


def load_response() -> dict:
    rows = list(csv.DictReader((RESULTS / 'paper_response_level_seeds.csv').open()))
    by_seed = {}
    for r in rows:
        by_seed.setdefault(int(r['seed']), {})[r['method']] = float(r['overall_accuracy'])
    def delta(a, b):
        return [v[a] - v[b] for _, v in sorted(by_seed.items())]
    return {
        'bayesian_vs_always_personalize': paired_summary(delta('bayesian_state', 'always_personalize_state')),
        'bayesian_vs_generic': paired_summary(delta('bayesian_state', 'generic')),
        'bayesian_vs_last_event': paired_summary(delta('bayesian_state', 'last_event')),
        'inferred_state_vs_last_event': paired_summary(delta('inferred_state', 'last_event')),
    }


def main() -> None:
    out = {
        'interpretation': (
            'Seed-level exact tests are deliberately conservative. With five non-tied paired seeds, '
            'even a 5/5 directional result has a two-sided exact sign-test p-value of 0.0625. '
            'These summaries therefore quantify consistency and effect size rather than licensing '
            'strong significance claims.'
        ),
        'mass_control': load_mass(),
        'response_level': load_response(),
    }
    (RESULTS / 'statistical_audit.json').write_text(json.dumps(out, indent=2) + '\n')

    m = out['mass_control']
    r = out['response_level']
    lines = [
        '# Statistical audit', '',
        'This audit treats independent benchmark seeds as the unit of replication for the repeated-seed headline comparisons. '
        'It is intentionally conservative: five seeds are useful for checking directional stability, but they are too few for strong asymptotic significance claims.', '',
        '## Exact paired-seed checks', '',
        '| Comparison | Mean paired delta | Wins / losses | Two-sided exact sign p | Paired effect dz |',
        '|---|---:|---:|---:|---:|',
    ]
    rows = [
        ('Raw synthetic − real-only', m['raw_vs_real_only']),
        ('Mass-capped − raw synthetic', m['mass_capped_vs_raw']),
        ('Mass-capped − real-only', m['mass_capped_vs_real_only']),
        ('Bayesian response − always-personalize', r['bayesian_vs_always_personalize']),
        ('Bayesian response − generic', r['bayesian_vs_generic']),
        ('Bayesian response − last-event', r['bayesian_vs_last_event']),
        ('Inferred-state response − last-event', r['inferred_state_vs_last_event']),
    ]
    for name, s in rows:
        dz = 'n/a' if s['paired_standardized_effect_dz'] is None else f"{s['paired_standardized_effect_dz']:.2f}"
        lines.append(f"| {name} | {s['mean_delta']:+.4f} | {s['wins']} / {s['losses']} | {s['exact_sign_test_two_sided_p']:.4f} | {dz} |")
    lines += [
        '',
        '## Interpretation', '',
        '- Raw synthetic augmentation is worse than real-only in all five seeds.',
        '- Mass capping improves over raw augmentation in all five seeds, but with only five paired seeds the two-sided exact sign test is still 0.0625. The release therefore describes this as a consistent mitigation, not a statistically definitive superiority claim.',
        '- Mass-capped augmentation is mixed relative to real-only (3 wins, 2 losses) and should not be described as an improvement over the real-only reference.',
        '- The Bayesian response policy beats always-personalize, generic, and last-event baselines in all five seeds. The repeated direction is encouraging, but the same five-seed limitation applies.',
        '- Inferred-state and last-event response policies are effectively tied at this replication level (3 wins, 2 losses, very small mean delta).', '',
        '## Why this file exists', '',
        'A small-seed research artifact can look more certain than it is if it reports only means. This audit keeps the unit of replication explicit and prevents seed-level consistency from being misreported as high-powered statistical evidence. User-level bootstrap intervals in the paper answer a different question: uncertainty over held-out examples conditional on the benchmark design.', '',
    ]
    (DOCS / 'statistical-audit.md').write_text('\n'.join(lines))

if __name__ == '__main__':
    main()
