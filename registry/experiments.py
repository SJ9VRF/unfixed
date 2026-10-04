from __future__ import annotations
import hashlib, json, platform, subprocess
from pathlib import Path
from typing import Any

class ExperimentRegistry:
    def __init__(self,path: str|Path='results/experiment_registry.jsonl'):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
    @staticmethod
    def _git_commit():
        try:return subprocess.check_output(['git','rev-parse','HEAD'],stderr=subprocess.DEVNULL,text=True).strip()
        except Exception:return None
    def log(self,name:str, config:dict[str,Any], metrics:dict[str,Any], artifacts:list[str]|None=None):
        canonical=json.dumps(config,sort_keys=True,default=str).encode()
        record={'run_id':hashlib.sha256(canonical+name.encode()).hexdigest()[:16],'name':name,'config':config,'metrics':metrics,'artifacts':artifacts or [],'git_commit':self._git_commit(),'python':platform.python_version()}
        with self.path.open('a',encoding='utf8') as f:f.write(json.dumps(record,sort_keys=True,default=str)+'\n')
        return record
