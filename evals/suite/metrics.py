from __future__ import annotations
from dataclasses import dataclass,asdict
import math

@dataclass
class AggregateMetrics:
    accuracy: float
    coverage: float
    calibration_error: float
    high_confidence_error_rate: float
    interactions_to_80pct: int | None = None
    def to_dict(self): return asdict(self)

def expected_calibration_error(conf_correct:list[tuple[float,int]],bins:int=10)->float:
    if not conf_correct:return 0.0
    total=len(conf_correct); ece=0.0
    for b in range(bins):
        lo=b/bins; hi=(b+1)/bins
        bucket=[(c,y) for c,y in conf_correct if lo<=c<hi or (b==bins-1 and c==1)]
        if bucket:
            avgc=sum(c for c,_ in bucket)/len(bucket); avga=sum(y for _,y in bucket)/len(bucket)
            ece += len(bucket)/total*abs(avgc-avga)
    return ece
