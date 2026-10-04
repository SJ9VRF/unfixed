from __future__ import annotations
import json
from collections import defaultdict,Counter
from pathlib import Path

def load(path='human_data/labels.jsonl'):
    p=Path(path)
    if not p.exists(): return []
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]

def pairwise_agreement(rows):
    by=defaultdict(list)
    for r in rows:
        if 'item_id' in r and 'annotator_id' in r: by[r['item_id']].append(r['winner'])
    pairs=[v for v in by.values() if len(v)>=2]
    return sum(len(set(v))==1 for v in pairs)/len(pairs) if pairs else None

if __name__=='__main__':
    rows=load(); print({'labels':len(rows),'exact_item_agreement':pairwise_agreement(rows)})
