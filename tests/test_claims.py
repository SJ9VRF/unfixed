import json
from pathlib import Path

def test_reference_claims_are_versioned_and_bounded():
    x=json.loads(Path('claims/reference_claims.json').read_text())
    assert x['version']=='0.5.0'
    assert 0 < x['tolerance'] <= 0.01
    assert len(x['claims']) >= 5
