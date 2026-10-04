from __future__ import annotations
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
EXCLUDE={'.pytest_cache','__pycache__','.git','pdf_render','.coverage'}
files=[]
for p in sorted(ROOT.rglob('*')):
    if not p.is_file() or any(x in EXCLUDE for x in p.parts) or p.name in EXCLUDE or p.suffix in {'.aux','.log','.out','.fls','.fdb_latexmk','.synctex.gz'}:continue
    if p.name=='MANIFEST.json':continue
    h=hashlib.sha256(p.read_bytes()).hexdigest();files.append({'path':str(p.relative_to(ROOT)),'sha256':h,'bytes':p.stat().st_size})
payload={'artifact':'The Unfixed User','version':'0.7.0','file_count':len(files),'files':files}
(ROOT/'MANIFEST.json').write_text(json.dumps(payload,indent=2))
print(f"Wrote MANIFEST.json with {len(files)} files")
