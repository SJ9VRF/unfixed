from __future__ import annotations
import csv,json,html
from pathlib import Path

def _table(rows, cols):
    return ''.join('<tr>'+''.join(f'<td>{html.escape(str(r.get(c,"")))}</td>' for c in cols)+'</tr>' for r in rows)

def build_dashboard():
    rows=list(csv.DictReader(open('results/benchmark.csv')))
    v2rows=list(csv.DictReader(open('results/v2_context_benchmark.csv'))) if Path('results/v2_context_benchmark.csv').exists() else []
    robust=json.loads(Path('results/robustness.json').read_text()) if Path('results/robustness.json').exists() else {}
    v3=json.loads(Path('results/v3_results.json').read_text()) if Path('results/v3_results.json').exists() else {}
    methods=sorted(set(r['method'] for r in rows))
    table=''.join(f"<tr><td>{html.escape(r['method'])}</td><td>{r['n_interactions']}</td><td>{float(r['accuracy']):.3f}</td><td>{float(r['coverage']):.3f}</td><td>{float(r['calibration_error']):.3f}</td><td>{float(r['high_confidence_error_rate']):.3f}</td></tr>" for r in rows)
    v2parts=[]
    for r in v2rows:
        g='-' if not r['global_accuracy'] else f"{float(r['global_accuracy']):.3f}"
        v2parts.append(f"<tr><td>{html.escape(r['method'])}</td><td>{r['n_interactions']}</td><td>{g}</td><td>{float(r['context_accuracy']):.3f}</td></tr>")
    v2table=''.join(v2parts)
    gate=robust.get('v2',{}).get('anti_personalization_gate',{})
    boundary=robust.get('v2',{}).get('boundary_selection',{})
    seed50=next((r for r in v3.get('seed_stability',{}).get('summary',[]) if r['n_interactions']==50),{})
    syn=v3.get('synthetic_downstream_utility',{}).get('summary',[])
    real=next((r for r in syn if r['method']=='real_only'),{})
    uncertainty=next((r for r in syn if r['method']=='uncertainty'),{})
    change=v3.get('change_detection',{})
    highlights=f"""<div class='grid'>
      <div class='card'><span>Context accuracy @50</span><h3>{seed50.get('mean_context_accuracy',0):.3f}</h3><p>mean across 5 seeds</p></div>
      <div class='card'><span>Semantic gate</span><h3>{gate.get('held_out_accuracy',0):.1%}</h3><p>Brier {gate.get('brier_score',0):.3f}</p></div>
      <div class='card'><span>Drift detection</span><h3>AUC {change.get('roc_auc',0):.3f}</h3><p>controlled reversal benchmark</p></div>
      <div class='card'><span>Synthetic utility</span><h3>{uncertainty.get('mean_context_accuracy',0):.3f}</h3><p>uncertainty vs real-only {real.get('mean_context_accuracy',0):.3f}</p></div>
    </div>"""
    seedrows=v3.get('seed_stability',{}).get('summary',[])
    synrows=syn
    noiserows=v3.get('noise_stress',[])
    style="""body{font-family:Inter,Arial,sans-serif;margin:0;background:#090b0f;color:#eef2f6}main{max-width:1180px;margin:auto;padding:56px 24px}h1{font-size:54px;margin:0 0 8px}.sub{color:#a9b2bf;font-size:20px;max-width:900px}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:32px 0}.card{background:#141922;border:1px solid #2a3240;border-radius:16px;padding:20px}.card span{color:#99a5b5;font-size:13px;text-transform:uppercase;letter-spacing:.08em}.card h3{font-size:30px;margin:8px 0}.card p{color:#a9b2bf;margin:0}table{width:100%;border-collapse:collapse;background:#11151c;margin:12px 0 34px}th,td{padding:11px;border-bottom:1px solid #28303d;text-align:left}th{background:#151922}pre{white-space:pre-wrap;background:#11151c;padding:18px;border-radius:12px;max-height:500px;overflow:auto}.note{border-left:3px solid #a9b2bf;padding:12px 18px;background:#11151c;color:#c7ced8}@media(max-width:800px){.grid{grid-template-columns:1fr 1fr}h1{font-size:42px}}"""
    doc=f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>The Unfixed User — Evaluation Dashboard</title><style>{style}</style></head><body><main><h1>The Unfixed User</h1><p class="sub">Self-evolving personalized agents from sparse feedback: context, calibration, drift, relevance gating, counterfactual experience and downstream utility evaluation.</p>{highlights}<div class="note"><b>Scientific contract:</b> synthetic examples are useful only if they improve held-out behavior. Boundary targeting alone is not counted as a win.</div><h2>Cold-start benchmark</h2><table><thead><tr><th>Method</th><th>Interactions</th><th>Accuracy</th><th>Coverage</th><th>ECE</th><th>High-conf error</th></tr></thead><tbody>{table}</tbody></table><h2>Context-conditioned benchmark</h2><table><thead><tr><th>Method</th><th>Interactions</th><th>Global accuracy</th><th>Context accuracy</th></tr></thead><tbody>{v2table}</tbody></table><h2>Repeated-seed stability</h2><table><thead><tr><th>Interactions</th><th>Mean</th><th>SE</th><th>CI low</th><th>CI high</th><th>Seeds</th></tr></thead><tbody>{_table(seedrows,['n_interactions','mean_context_accuracy','standard_error','ci95_low','ci95_high','n_seeds'])}</tbody></table><h2>Synthetic data: downstream utility</h2><table><thead><tr><th>Method</th><th>Mean context accuracy</th><th>CI low</th><th>CI high</th></tr></thead><tbody>{_table(synrows,['method','mean_context_accuracy','ci95_low','ci95_high'])}</tbody></table><h2>Noise stress</h2><table><thead><tr><th>Noise</th><th>Mean accuracy</th><th>CI low</th><th>CI high</th></tr></thead><tbody>{_table(noiserows,['noise','mean_global_accuracy','ci95_low','ci95_high'])}</tbody></table><h2>Full diagnostics</h2><pre>{html.escape(json.dumps(v3,indent=2))}</pre></main></body></html>'''
    Path('dashboard').mkdir(exist_ok=True);Path('dashboard/index.html').write_text(doc)
    return 'dashboard/index.html'
