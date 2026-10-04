from __future__ import annotations
from dataclasses import dataclass

@dataclass
class CalibrationReport:
    n:int; agreement:float; false_positive_rate:float; false_negative_rate:float

def calibrate(human:list[int],grader:list[int])->CalibrationReport:
    if len(human)!=len(grader): raise ValueError('label lengths differ')
    n=len(human)
    if not n:return CalibrationReport(0,0,0,0)
    agree=sum(a==b for a,b in zip(human,grader))/n
    neg=sum(x==0 for x in human); pos=sum(x==1 for x in human)
    fp=sum(h==0 and g==1 for h,g in zip(human,grader))/max(1,neg)
    fn=sum(h==1 and g==0 for h,g in zip(human,grader))/max(1,pos)
    return CalibrationReport(n,agree,fp,fn)
