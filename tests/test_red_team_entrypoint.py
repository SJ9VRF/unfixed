import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_red_team_direct_entrypoint_runs():
    p = subprocess.run([sys.executable, str(ROOT/'red_team'/'suite.py')], cwd=ROOT, text=True, capture_output=True)
    assert p.returncode == 0, p.stderr
    assert '"ok": true' in p.stdout
