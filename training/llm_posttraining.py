from __future__ import annotations
"""External open-weight post-training entry point.

This module is intentionally dependency-gated.  It creates auditable SFT JSONL
from the project's interaction format and, when transformers/peft are installed,
provides the configuration boundary for LoRA/SFT.  The reference release does not
claim a model run unless those dependencies, weights, and resulting checkpoints
are present in the experiment registry.
"""
import json
from pathlib import Path

def build_sft_jsonl(examples:list[dict], out_path:str|Path):
    path=Path(out_path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8') as f:
        for ex in examples:
            required={'history','query','response'}
            if not required.issubset(ex): raise ValueError(f'missing SFT fields: {required-set(ex)}')
            f.write(json.dumps({'messages':[{'role':'system','content':'Personalize only from supported user evidence.'},
                                            {'role':'user','content':ex['history']+'\n\n'+ex['query']},
                                            {'role':'assistant','content':ex['response']}],
                                'metadata':ex.get('metadata',{})},ensure_ascii=False)+'\n')
    return path

def dependency_status():
    status={}
    for name in ('torch','transformers','peft','datasets'):
        try:
            mod=__import__(name); status[name]={'available':True,'version':getattr(mod,'__version__','unknown')}
        except Exception as e: status[name]={'available':False,'reason':type(e).__name__}
    return status

if __name__=='__main__':
    print(json.dumps(dependency_status(),indent=2))
