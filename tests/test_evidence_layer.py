from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_evidence_layer_core_files_exist():
    for rel in [
        'docs/evidence-layer.md','docs/experiment-log.md','docs/failed-experiments.md',
        'docs/decision-log.md','docs/eval-tables.md','docs/unexpected-findings.md',
        'docs/failure-trace.md','docs/git-provenance.md'
    ]:
        assert (ROOT/rel).is_file(), rel

def test_experiment_log_has_13_real_entries():
    text=(ROOT/'docs/experiment-log.md').read_text()
    for i in range(1,14):
        assert f'EXP-{i:03d}' in text

def test_raw_evidence_tree_present():
    for rel in ['experiment_logs','eval_runs','failure_examples','plots','configs','qualitative_cases','ablations']:
        p=ROOT/'artifacts'/rel
        assert p.is_dir() and any(x.is_file() for x in p.rglob('*')), rel

def test_homepage_exposes_research_process():
    text=(ROOT/'portfolio/index.html').read_text()
    assert 'id="research-process"' in text
    assert '13</b><span>documented experiments' in text
    assert '../docs/experiment-log.md' in text
    assert '../docs/failed-experiments.md' in text
    assert '../docs/failure-trace.md' in text

def test_git_history_is_not_fabricated():
    text=(ROOT/'docs/git-provenance.md').read_text().lower()
    assert 'does **not** backfill a fake commit history' in text
