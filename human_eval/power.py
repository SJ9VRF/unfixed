from __future__ import annotations
import json, math
from pathlib import Path
from scipy.stats import norm

def proportion_power_n(p0=.5,p1=.6,alpha=.05,power=.8):
    za=norm.ppf(1-alpha/2); zb=norm.ppf(power)
    n=((za*math.sqrt(p0*(1-p0))+zb*math.sqrt(p1*(1-p1)))**2)/((p1-p0)**2)
    return math.ceil(n)

def build(out='human_eval/power_analysis.json'):
    effects=[.56,.58,.60,.62,.65]
    payload={'null_pairwise_win_rate':.5,'alpha_two_sided':.05,'target_power':.8,
             'judgments_required':{str(p):proportion_power_n(.5,p) for p in effects},
             'note':'Independent-judgment approximation. A recruited study with repeated judgments per participant should inflate for clustering and report participant-level uncertainty.'}
    Path(out).write_text(json.dumps(payload,indent=2));return payload
if __name__=='__main__':print(json.dumps(build(),indent=2))
