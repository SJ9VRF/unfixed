from __future__ import annotations
import random, math
from typing import Iterable


def mean(xs: Iterable[float]) -> float:
    xs=list(xs); return sum(xs)/max(1,len(xs))


def bootstrap_ci(values:list[float], confidence:float=.95, n_boot:int=2000, seed:int=0)->tuple[float,float]:
    if not values: return (float('nan'),float('nan'))
    if len(values)==1: return (values[0],values[0])
    rng=random.Random(seed); n=len(values); samples=[]
    for _ in range(n_boot):
        samples.append(sum(values[rng.randrange(n)] for _ in range(n))/n)
    samples.sort(); alpha=(1-confidence)/2
    lo=samples[max(0,min(len(samples)-1,int(alpha*len(samples))))]
    hi=samples[max(0,min(len(samples)-1,int((1-alpha)*len(samples))-1))]
    return lo,hi


def paired_bootstrap_delta(a:list[float], b:list[float], n_boot:int=3000, seed:int=0)->dict:
    if len(a)!=len(b) or not a: raise ValueError('paired arrays must be non-empty and equal length')
    diffs=[x-y for x,y in zip(a,b)]; obs=mean(diffs); lo,hi=bootstrap_ci(diffs,n_boot=n_boot,seed=seed)
    rng=random.Random(seed+1); n=len(diffs); boot=[]
    for _ in range(n_boot): boot.append(mean([diffs[rng.randrange(n)] for _ in range(n)]))
    # two-sided bootstrap sign probability around zero; descriptive, not a parametric p-value.
    p=2*min(sum(x<=0 for x in boot)/len(boot),sum(x>=0 for x in boot)/len(boot))
    return {'mean_delta':obs,'ci95':[lo,hi],'bootstrap_two_sided_p':min(1.0,p)}


def standard_error(values:list[float])->float:
    if len(values)<2:return 0.0
    m=mean(values); var=sum((x-m)**2 for x in values)/(len(values)-1)
    return math.sqrt(var/len(values))
