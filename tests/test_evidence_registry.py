from pathlib import Path
import hashlib, json, re

ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/'artifacts/evidence_registry.json'

def digest(p:Path)->str:
    h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()

def test_registry_is_complete_and_hashes_match():
    r=json.loads(REG.read_text())
    assert r['project']=='The Unfixed User'
    assert r['author']=='Aura Yavary'
    assert r['counts']=={'experiments':13,'failed_hypotheses':5,'major_decisions':6,'primary_failure_modes':4}
    assert [e['id'] for e in r['experiments']]==[f'EXP-{i:03d}' for i in range(1,14)]
    for e in r['experiments']:
        assert e['raw_evidence'], e['id']
        assert e['reproduce'].startswith('python scripts/run_experiment.py ')
        for group in ('code','configs','raw_evidence'):
            for x in e[group]:
                p=ROOT/x['path']; assert p.is_file(), (e['id'],x['path'])
                assert digest(p)==x['sha256'], (e['id'],x['path'])

def test_homepage_counts_match_registry():
    r=json.loads(REG.read_text())['counts']
    page=(ROOT/'portfolio/index.html').read_text()
    expected=[
        (r['experiments'],'documented experiments'),
        (r['failed_hypotheses'],'failed hypotheses kept'),
        (r['major_decisions'],'major research decisions'),
        (r['primary_failure_modes'],'primary failure modes'),
    ]
    for n,label in expected:
        assert f'<b>{n}</b><span>{label}</span>' in page

def test_experiment_journal_has_canonical_reproduce_command_for_every_entry():
    r=json.loads(REG.read_text())
    text=(ROOT/'docs/experiment-log.md').read_text()
    for e in r['experiments']:
        assert f'## {e["id"]}' in text
        assert f'`{e["reproduce"]}`' in text

def test_registry_builder_references_all_experiments():
    text=(ROOT/'scripts/build_evidence_registry.py').read_text()
    for i in range(1,14):
        assert f"'EXP-{i:03d}'" in text
