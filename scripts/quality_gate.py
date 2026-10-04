from __future__ import annotations
import compileall, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return {
        'cmd': ' '.join(cmd),
        'returncode': p.returncode,
        'stdout': p.stdout[-8000:],
        'stderr': p.stderr[-8000:],
    }


def main():
    checks = []
    checks.append({'name': 'compileall', 'ok': compileall.compile_dir(str(ROOT), quiet=1)})

    # Coverage-enabled pytest already executes the full test suite; running pytest
    # once more adds time without increasing the release contract.
    r = run([
        sys.executable, '-m', 'pytest',
        '--cov=.', '--cov-report=term-missing:skip-covered',
        '--cov-fail-under=70', '-q'
    ])
    checks.append({'name': 'tests_and_coverage', 'ok': r['returncode'] == 0, **r})

    from red_team.suite import run_red_team
    rt = run_red_team()
    checks.append({'name': 'red_team', 'ok': rt['ok'], 'detail': rt})

    out = {'ok': all(c['ok'] for c in checks), 'checks': checks}
    (ROOT / 'results').mkdir(exist_ok=True)
    (ROOT / 'results' / 'quality_gate.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'ok': out['ok'], 'checks': [{k: v for k, v in c.items() if k in ('name', 'ok')} for c in checks]}, indent=2))
    raise SystemExit(0 if out['ok'] else 1)


if __name__ == '__main__':
    main()
