from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
ref=json.loads((ROOT/'claims/paper_claims.json').read_text())
res=json.loads((ROOT/'results/paper_results.json').read_text())
summary={x['method']:x['accuracy'] for x in res['oracle_vs_pseudo']['summary']}
stats=res['oracle_vs_pseudo']['label_stats']
rows=[x for x in res['synthetic_mass_sweep'] if x['k']>0]
xs=[x['synthetic_mass'] for x in rows]; ys=[x['delta_vs_real'] for x in rows]
mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
corr=sum((a-mx)*(b-my) for a,b in zip(xs,ys))/(sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))**.5
mc=res['mass_aware_mitigation']; rls={x['method']:x for x in res['response_level']['summary']}
rr=json.loads((ROOT/'results/paper_response_level_repeated.json').read_text()); rlr={x['method']:x for x in rr['summary']}
actual={
 'oracle_vs_pseudo': {'real_only_accuracy':summary['real_only'],'pseudo_accuracy':summary['pseudo'],'oracle_accuracy':summary['oracle'],'uces_accuracy':summary['uces'],'pseudo_label_error_rate':stats['pseudo_label_error_rate'],'uces_label_error_rate':stats['uces_label_error_rate']},
 'synthetic_mass': {'correlation_mass_vs_delta':corr,'worst_delta':min(ys)},
 'drift_auc': {x['method']:x['roc_auc'] for x in res['drift_baselines']},
 'mass_control': {'fraction_harm_recovered':mc['fraction_harm_recovered'],'mass_capped_accuracy':next(x['mean_accuracy'] for x in mc['summary'] if x['method']=='mass_capped_uces'),'raw_uces_accuracy':next(x['mean_accuracy'] for x in mc['summary'] if x['method']=='uces_raw')},
 'response_level': {'bayesian_overall_accuracy':rls['bayesian_state']['overall_accuracy'],'always_personalize_overall_accuracy':rls['always_personalize_state']['overall_accuracy'],'always_personalize_overpersonalization_rate':rls['always_personalize_state']['overpersonalization_rate'],'neural_ranker_accuracy':rls['neural_response_ranker']['overall_accuracy']},
 'response_level_repeated': {'bayesian_overall_accuracy_mean':rlr['bayesian_state']['overall_accuracy_mean'],'bayesian_overall_accuracy_sd':rlr['bayesian_state']['overall_accuracy_sd'],'always_personalize_overall_accuracy_mean':rlr['always_personalize_state']['overall_accuracy_mean'],'always_personalize_overpersonalization_rate_mean':rlr['always_personalize_state']['overpersonalization_rate_mean'],'generic_overall_accuracy_mean':rlr['generic']['overall_accuracy_mean'],'neural_ranker_accuracy_mean':rlr['neural_response_ranker']['overall_accuracy_mean'],'neural_ranker_accuracy_sd':rlr['neural_response_ranker']['overall_accuracy_sd']},
}
fail=[]
for group, vals in ref.items():
    for key, exp in vals.items():
        got=actual[group][key]
        if abs(got-exp)>1e-9: fail.append((group,key,exp,got))
if fail:
    for x in fail: print('FAIL',x)
    raise SystemExit(1)
print('Paper claims verified:',sum(len(v) for v in ref.values()),'claims')
