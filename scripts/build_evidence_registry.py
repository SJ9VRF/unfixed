from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / 'artifacts' / 'experiment_logs'
OUT = ROOT / 'artifacts' / 'evidence_registry.json'

CODE = {
 'EXP-001':['evals/suite/runner.py'],
 'EXP-002':['evals/suite/v2_runner.py'],
 'EXP-003':['evals/suite/v3_runner.py'],
 'EXP-004':['evals/suite/v2_runner.py','synthetic_experience/selection/engine.py'],
 'EXP-005':['evals/suite/v3_runner.py'],
 'EXP-006':['evals/suite/paper_runner.py'],
 'EXP-007':['evals/suite/paper_runner.py'],
 'EXP-008':['evals/suite/paper_runner.py','synthetic_experience/mass_control.py'],
 'EXP-009':['evals/suite/paper_runner.py'],
 'EXP-010':['evals/suite/v3_runner.py'],
 'EXP-011':['evals/suite/paper_runner.py','user_model/probabilistic.py'],
 'EXP-012':['evals/response_level/repeated.py','evals/response_level/benchmark.py'],
 'EXP-013':['evals/suite/paper_runner.py'],
}
CONFIG = {
 'EXP-001':['artifacts/configs/cold_start.json'],
 'EXP-002':[],
 'EXP-003':['artifacts/configs/seed_stability.json'],
 'EXP-004':[],
 'EXP-005':['artifacts/configs/synthetic_utility.json'],
 'EXP-006':['artifacts/configs/oracle_diagnostic.json'],
 'EXP-007':['artifacts/configs/mass_sweep.json'],
 'EXP-008':['artifacts/configs/mass_control.json'],
 'EXP-009':[],
 'EXP-010':[],
 'EXP-011':[],
 'EXP-012':['artifacts/configs/response_level.json'],
 'EXP-013':[],
}
LINKS = {
 'EXP-001':{'decisions':[],'failures':[]},
 'EXP-002':{'decisions':[],'failures':[]},
 'EXP-003':{'decisions':[],'failures':[]},
 'EXP-004':{'decisions':['D-001'],'failures':['F-003']},
 'EXP-005':{'decisions':['D-001'],'failures':['F-001','F-003']},
 'EXP-006':{'decisions':['D-002'],'failures':['F-002']},
 'EXP-007':{'decisions':['D-003'],'failures':[]},
 'EXP-008':{'decisions':['D-003'],'failures':[]},
 'EXP-009':{'decisions':['D-005'],'failures':['F-004']},
 'EXP-010':{'decisions':[],'failures':[]},
 'EXP-011':{'decisions':['D-004'],'failures':[]},
 'EXP-012':{'decisions':['D-004'],'failures':['F-005']},
 'EXP-013':{'decisions':[],'failures':[]},
}

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()

def rec(rel: str) -> dict:
    p=ROOT/rel
    return {'path':rel,'sha256':sha256(p),'bytes':p.stat().st_size}

def build() -> dict:
    experiments=[]
    for p in sorted(LOG_DIR.glob('exp-*.json')):
        log=json.loads(p.read_text())
        exp_id=log['id']
        raw=[rec(x) for x in log.get('raw',[])]
        code=[rec(x) for x in CODE[exp_id]]
        configs=[rec(x) for x in CONFIG[exp_id]]
        experiments.append({
            'id':exp_id,
            'title':log['title'],
            'status':log['status'],
            'hypothesis':log['hypothesis'],
            'reproduce':f'python scripts/run_experiment.py {exp_id} --out scratch/{exp_id.lower()}',
            'code':code,
            'configs':configs,
            'raw_evidence':raw,
            **LINKS[exp_id],
        })
    payload={
        'project':'The Unfixed User',
        'author':'Aura Yavary',
        'counts':{
            'experiments':len(experiments),
            'failed_hypotheses':5,
            'major_decisions':6,
            'primary_failure_modes':4,
        },
        'experiments':experiments,
        'policy':{
            'timestamps':'omitted',
            'git_history':'not reconstructed',
            'external_results':'not populated unless actually executed',
        },
    }
    OUT.write_text(json.dumps(payload,indent=2)+'\n')
    return payload

if __name__=='__main__':
    p=build()
    print(f"wrote {OUT.relative_to(ROOT)} with {len(p['experiments'])} experiments")
