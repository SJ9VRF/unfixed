from __future__ import annotations
import csv
from pathlib import Path
import matplotlib.pyplot as plt

def main():
    out=Path('results/figures'); out.mkdir(parents=True,exist_ok=True)
    rows=list(csv.DictReader(open('results/benchmark.csv')))
    methods=sorted(set(r['method'] for r in rows))
    plt.figure(figsize=(8,5))
    for m in methods:
        rr=[r for r in rows if r['method']==m]
        plt.plot([int(r['n_interactions']) for r in rr],[float(r['accuracy']) for r in rr],marker='o',label=m.replace('_',' '))
    plt.xlabel('Real interactions'); plt.ylabel('Preference-state accuracy'); plt.ylim(0,1.02); plt.title('Cold-start personalization'); plt.legend(); plt.tight_layout(); plt.savefig(out/'cold_start_accuracy.png',dpi=180); plt.close()
    plt.figure(figsize=(8,5))
    for m in methods:
        rr=[r for r in rows if r['method']==m]
        plt.plot([int(r['n_interactions']) for r in rr],[float(r['calibration_error']) for r in rr],marker='o',label=m.replace('_',' '))
    plt.xlabel('Real interactions'); plt.ylabel('Expected calibration error'); plt.title('Confidence calibration'); plt.legend(); plt.tight_layout(); plt.savefig(out/'calibration.png',dpi=180); plt.close()
    sel=list(csv.DictReader(open('results/selection_ablation.csv')))
    plt.figure(figsize=(9,5)); plt.bar([r['policy'].replace('_','\n') for r in sel],[float(r['mean_verified_information_value']) for r in sel]); plt.ylabel('Verified information value'); plt.title('Synthetic experience selection ablation'); plt.tight_layout(); plt.savefig(out/'selection_ablation.png',dpi=180); plt.close()
    v2=list(csv.DictReader(open('results/v2_context_benchmark.csv')))
    plt.figure(figsize=(8,5))
    for m in sorted(set(r['method'] for r in v2)):
        rr=[r for r in v2 if r['method']==m]
        plt.plot([int(r['n_interactions']) for r in rr],[float(r['context_accuracy']) for r in rr],marker='o',label=m.replace('_',' '))
    plt.xlabel('Real interactions'); plt.ylabel('Context-conditioned accuracy'); plt.ylim(0,1.02); plt.title('Learning context-dependent preferences'); plt.legend(); plt.tight_layout(); plt.savefig(out/'context_accuracy.png',dpi=180); plt.close()

    # V3 repeated-seed stability with 95% bootstrap intervals.
    if Path('results/v3_seed_summary.csv').exists():
        ss=list(csv.DictReader(open('results/v3_seed_summary.csv')))
        xs=[int(r['n_interactions']) for r in ss]; ys=[float(r['mean_context_accuracy']) for r in ss]
        lo=[y-float(r['ci95_low']) for y,r in zip(ys,ss)]; hi=[float(r['ci95_high'])-y for y,r in zip(ys,ss)]
        plt.figure(figsize=(8,5)); plt.errorbar(xs,ys,yerr=[lo,hi],marker='o',capsize=4)
        plt.xlabel('Real interactions'); plt.ylabel('Mean context accuracy'); plt.ylim(0,1.02); plt.title('Repeated-seed stability (95% bootstrap CI)'); plt.tight_layout(); plt.savefig(out/'seed_stability.png',dpi=180); plt.close()
    if Path('results/v3_synthetic_utility.csv').exists():
        su=list(csv.DictReader(open('results/v3_synthetic_utility.csv')))
        plt.figure(figsize=(10,5)); plt.bar([r['method'].replace('_','\n') for r in su],[float(r['mean_context_accuracy']) for r in su])
        plt.ylabel('Context accuracy @ 10 interactions'); plt.title('Downstream utility of synthetic selection policies'); plt.tight_layout(); plt.savefig(out/'synthetic_downstream_utility.png',dpi=180); plt.close()
    if Path('results/v3_noise_stress.csv').exists():
        ns=list(csv.DictReader(open('results/v3_noise_stress.csv')))
        plt.figure(figsize=(8,5)); plt.plot([float(r['noise']) for r in ns],[float(r['mean_global_accuracy']) for r in ns],marker='o')
        plt.xlabel('Observation noise'); plt.ylabel('Global preference accuracy'); plt.ylim(0,1.02); plt.title('Noise stress test'); plt.tight_layout(); plt.savefig(out/'noise_stress.png',dpi=180); plt.close()

if __name__=='__main__':main()

# V3 figures are appended through a wrapper below.
