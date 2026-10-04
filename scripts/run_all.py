from __future__ import annotations
import sys, os, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
os.chdir(ROOT)
from evals.suite.runner import run_full_benchmark
from evals.suite.v2_runner import run_v2_benchmark
from evals.suite.v3_runner import run_v3_benchmark
from evals.drift.run import evaluate_drift
from evals.conflicts.run import evaluate_conflicts
from evals.anti_personalization.run import evaluate_anti_personalization
from evals.long_horizon.run import evaluate_long_horizon
from dashboard.build import build_dashboard
from human_eval.build_study import build as build_human_study
from evals.suite.paper_runner import run_paper_suite

def main():
    Path('results').mkdir(exist_ok=True)
    run_full_benchmark('results')
    v2=run_v2_benchmark('results')
    v3=run_v3_benchmark('results')
    paper=run_paper_suite('results')
    extra={'drift':evaluate_drift(),'conflicts':evaluate_conflicts(),'anti_personalization':evaluate_anti_personalization(),'long_horizon':evaluate_long_horizon(),'v2':v2,'v3':v3,'paper':paper}
    Path('results/robustness.json').write_text(json.dumps(extra,indent=2))
    from scripts.build_figures import main as build_figures
    build_figures()
    from scripts.build_paper_figures import __file__ as _paper_fig_script
    import runpy
    runpy.run_path(_paper_fig_script, run_name='__main__')
    build_dashboard()
    build_human_study(Path('human_eval/study_items.csv'))
    from registry.experiments import ExperimentRegistry
    registry=ExperimentRegistry('results/experiment_registry.jsonl')
    registry.path.write_text('')
    registry.log('v5_full_benchmark', {'offline': True, 'suite': 'v1-v3+robustness', 'version': '0.5.0'}, {'status': 'completed'}, ['results/v3_results.json','results/robustness.json','dashboard/index.html'])
    from scripts.verify_claims import main as verify_claims
    try: verify_claims()
    except SystemExit as e:
        if e.code: raise
    print('Completed The Unfixed User V6 benchmark. Outputs: results/, results/figures/, dashboard/index.html, human_eval/study_items.csv')
if __name__=='__main__':main()
