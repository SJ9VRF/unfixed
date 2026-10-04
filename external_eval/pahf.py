from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class PAHFScenario:
    index: int
    user: str
    task: str
    context: str
    scene: str
    target: str | None

def load_pahf_scenarios(path:str|Path)->list[PAHFScenario]:
    data=json.loads(Path(path).read_text(encoding='utf-8'))
    if isinstance(data,dict):
        for key in ('scenarios','data','items'):
            if key in data: data=data[key]; break
    out=[]
    for i,row in enumerate(data):
        target=row.get('user_intent_object') or row.get('target') or row.get('answer')
        out.append(PAHFScenario(int(row.get('index',i)),str(row.get('user','')),str(row.get('task','')),
                                str(row.get('context','')),str(row.get('scene','')),None if target is None else str(target)))
    return out
