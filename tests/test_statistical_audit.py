import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_statistical_audit_exists_and_is_conservative():
    p = ROOT / 'results' / 'statistical_audit.json'
    data = json.loads(p.read_text())
    mass = data['mass_control']
    assert mass['mass_capped_vs_raw']['wins'] == 5
    assert mass['mass_capped_vs_raw']['losses'] == 0
    assert abs(mass['mass_capped_vs_raw']['exact_sign_test_two_sided_p'] - 0.0625) < 1e-12
    assert mass['mass_capped_vs_real_only']['wins'] == 3
    assert mass['mass_capped_vs_real_only']['losses'] == 2


def test_response_seed_audit_keeps_near_tie_visible():
    data = json.loads((ROOT / 'results' / 'statistical_audit.json').read_text())
    resp = data['response_level']
    assert resp['bayesian_vs_always_personalize']['wins'] == 5
    assert resp['inferred_state_vs_last_event']['wins'] == 3
    assert resp['inferred_state_vs_last_event']['losses'] == 2
