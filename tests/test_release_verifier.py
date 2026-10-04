from __future__ import annotations
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_release_verifier_script_exists_and_is_read_only_by_construction():
    p = ROOT / 'scripts' / 'verify_release.py'
    assert p.exists()
    text = p.read_text()
    assert 'write_text(' not in text
    assert 'MANIFEST.json' in text
    assert 'Aura Yavary' in text


def test_make_verify_builds_manifest_last():
    text = (ROOT / 'Makefile').read_text()
    block = text.split('\nverify:\n', 1)[1].split('\n\n', 1)[0]
    manifest_idx = block.index('build_manifest.py')
    for token in ['frontier_eval.run_reference', 'quality_gate.py', 'verify_paper_claims.py', 'verify_claims.py', 'statistical_audit.py', 'model_change_gate.py']:
        assert block.index(token) < manifest_idx


def test_reproducibility_doc_separates_verification_from_regeneration():
    text = (ROOT / 'REPRODUCIBILITY.md').read_text().lower()
    assert 'does **not** silently regenerate' in text
    assert 'make benchmark' in text
    assert 'python scripts/verify_release.py' in text
