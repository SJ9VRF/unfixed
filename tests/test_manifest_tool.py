from pathlib import Path

def test_manifest_verifier_exists():
    assert Path('scripts/verify_manifest.py').is_file()
