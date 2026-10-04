from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def closest(df,col,val): return df.iloc[(df[col]-val).abs().argsort()[:1]]

def main():
    spec=json.loads((ROOT/'claims/reference_claims.json').read_text()); tol=float(spec['tolerance']); exp=spec['claims']
    seed=pd.read_csv(ROOT/'results/v3_seed_summary.csv')
    util=pd.read_csv(ROOT/'results/v3_synthetic_utility.csv')
    noise=pd.read_csv(ROOT/'results/v3_noise_stress.csv')
    s50=seed[seed['n_interactions']==50]
    mean_col='mean_context_accuracy' if 'mean_context_accuracy' in s50.columns else [c for c in s50.columns if 'mean' in c and 'accuracy' in c][0]
    actual={'context_accuracy_50_mean':float(s50.iloc[0][mean_col])}
    # utility supports either rows by policy or columns by policy depending on saved version
    method_col='policy' if 'policy' in util.columns else ('method' if 'method' in util.columns else None)
    if method_col:
        value_col=[c for c in util.columns if 'accuracy' in c][-1]
        for key,policy in [('synthetic_real_only_10','real_only'),('synthetic_uncertainty_10','uncertainty'),('synthetic_decision_boundary_10','decision_boundary')]:
            row=util[util[method_col].astype(str)==policy]
            actual[key]=float(row.iloc[0][value_col])
    else:
        raise RuntimeError('unexpected synthetic utility schema')
    noise_col='noise'; acc_col=[c for c in noise.columns if 'accuracy' in c][0]
    actual['noise_0_accuracy']=float(closest(noise,noise_col,0.0).iloc[0][acc_col])
    actual['noise_032_accuracy']=float(closest(noise,noise_col,0.32).iloc[0][acc_col])
    checks={k:{'expected':exp[k],'actual':v,'delta':v-exp[k],'ok':abs(v-exp[k])<=tol} for k,v in actual.items()}
    out={'ok':all(v['ok'] for v in checks.values()),'tolerance':tol,'checks':checks}
    (ROOT/'results/claim_verification.json').write_text(json.dumps(out,indent=2))
    print(json.dumps(out,indent=2)); raise SystemExit(0 if out['ok'] else 1)
if __name__=='__main__':main()
