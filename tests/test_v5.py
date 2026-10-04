from interaction_engine.models import InteractionEvent
from validation.checks import validate_event,validate_dataset_rows
from privacy.redaction import redact_mapping
from red_team.suite import run_red_team
from registry.experiments import ExperimentRegistry

def test_validation_rejects_secret_metadata():
    e=InteractionEvent(event_id='1',user_id='u',preference_key='tone',observed_value='short',metadata={'api_key':'x'})
    assert any('sensitive metadata' in x for x in validate_event(e))

def test_dataset_duplicate_detection():
    r=validate_dataset_rows([{'event_id':'x','preference_key':'p'},{'event_id':'x','preference_key':'p'}])
    assert r['duplicate_event_ids']==['x'] and not r['ok']

def test_recursive_redaction():
    x=redact_mapping({'nested':{'password':'hello'},'text':'123-45-6789'})
    assert x['nested']['password']=='[REDACTED]' and x['text']=='[REDACTED]'

def test_red_team_suite_passes():
    r=run_red_team(); assert r['ok'] and r['passed']==r['total']

def test_experiment_registry(tmp_path):
    reg=ExperimentRegistry(tmp_path/'runs.jsonl'); rec=reg.log('x',{'seed':1},{'acc':.8},['a.csv'])
    assert rec['name']=='x' and (tmp_path/'runs.jsonl').exists()
