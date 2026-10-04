from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    m=json.loads((ROOT/'MANIFEST.json').read_text()); failures=[]
    for rec in m['files']:
        p=ROOT/rec['path']
        if not p.exists(): failures.append({'path':rec['path'],'error':'missing'}); continue
        h=hashlib.sha256(p.read_bytes()).hexdigest()
        if h!=rec['sha256'] or p.stat().st_size!=rec['bytes']:
            failures.append({'path':rec['path'],'error':'mismatch'})
    print(json.dumps({'ok':not failures,'version':m.get('version'),'checked':len(m['files']),'failures':failures},indent=2))
    raise SystemExit(0 if not failures else 1)
if __name__=='__main__': main()
