from pathlib import Path
import csv, json
import matplotlib.pyplot as plt
plt.rcParams['pdf.fonttype']=42
plt.rcParams['ps.fonttype']=42
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'results'/'paper_figures'; OUT.mkdir(parents=True,exist_ok=True)

def readcsv(name):
    with open(ROOT/'results'/name,newline='') as f:return list(csv.DictReader(f))

# synthetic mass / harm
rows=readcsv('paper_synthetic_mass_sweep.csv'); rows=[r for r in rows if int(r['k'])>0]
fig,ax=plt.subplots(figsize=(5.1,3.15))
for k in sorted(set(int(r['k']) for r in rows)):
    rr=[r for r in rows if int(r['k'])==k]
    ax.plot([float(r['synthetic_mass']) for r in rr],[100*float(r['delta_vs_real']) for r in rr],marker='o',label=f'k={k}')
ax.axhline(0,linewidth=1); ax.set_xlabel('Synthetic evidence mass (k × reliability)'); ax.set_ylabel('Δ context accuracy (pp)'); ax.legend(ncol=3,fontsize=8); fig.tight_layout(); fig.savefig(OUT/'synthetic_mass_harm.pdf'); fig.savefig(OUT/'synthetic_mass_harm.png',dpi=180); plt.close(fig)

# risk coverage
rows=readcsv('paper_risk_coverage.csv');
fig,ax=plt.subplots(figsize=(4.7,3.1)); ax.plot([100*float(r['coverage']) for r in rows],[100*float(r['risk']) for r in rows],marker='o'); ax.set_xlabel('Personalization coverage (%)'); ax.set_ylabel('Error among personalized cases (%)'); fig.tight_layout(); fig.savefig(OUT/'risk_coverage.pdf'); fig.savefig(OUT/'risk_coverage.png',dpi=180); plt.close(fig)

# regret
rows=readcsv('paper_regret.csv');
fig,ax=plt.subplots(figsize=(4.7,3.1)); ax.plot([int(r['n_interactions']) for r in rows],[float(r['mean_regret']) for r in rows],marker='o'); ax.fill_between([int(r['n_interactions']) for r in rows],[float(r['ci95_low']) for r in rows],[float(r['ci95_high']) for r in rows],alpha=.18); ax.set_xlabel('Real interactions'); ax.set_ylabel('Personalization regret'); fig.tight_layout(); fig.savefig(OUT/'regret_curve.pdf'); fig.savefig(OUT/'regret_curve.png',dpi=180); plt.close(fig)

# oracle/pseudo
rows=readcsv('paper_oracle_vs_pseudo.csv');
fig,ax=plt.subplots(figsize=(4.7,3.1)); labels=[r['method'].replace('_',' ') for r in rows]; vals=[float(r['accuracy']) for r in rows]; ax.bar(labels,vals); ax.set_ylim(min(vals)-.03,max(vals)+.03); ax.set_ylabel('Context accuracy'); ax.tick_params(axis='x',rotation=20); fig.tight_layout(); fig.savefig(OUT/'oracle_pseudo.pdf'); fig.savefig(OUT/'oracle_pseudo.png',dpi=180); plt.close(fig)

# mass-aware mitigation
rows=readcsv('paper_mass_control.csv')
fig,ax=plt.subplots(figsize=(4.9,3.1)); labels=[r['method'].replace('_',' ') for r in rows]; vals=[float(r['mean_accuracy']) for r in rows];
ax.bar(labels,vals); ax.set_ylim(min(vals)-.02,max(vals)+.02); ax.set_ylabel('Context accuracy'); ax.tick_params(axis='x',rotation=18); fig.tight_layout(); fig.savefig(OUT/'mass_control.pdf'); fig.savefig(OUT/'mass_control.png',dpi=180); plt.close(fig)

# response-level choice accuracy
rows=readcsv('paper_response_level_repeated.csv')
keep=[r for r in rows if r['method'] in {'generic','always_personalize_state','bayesian_state','structured_learner','neural_response_ranker'}]
fig,ax=plt.subplots(figsize=(5.2,3.2)); labels=[r['method'].replace('_',' ') for r in keep]; vals=[float(r['overall_accuracy_mean']) for r in keep]
ax.bar(labels,vals); ax.set_ylim(0,1); ax.set_ylabel('Response-choice accuracy'); ax.tick_params(axis='x',rotation=20); fig.tight_layout(); fig.savefig(OUT/'response_level.pdf'); fig.savefig(OUT/'response_level.png',dpi=180); plt.close(fig)
