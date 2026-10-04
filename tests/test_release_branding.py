from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OLD_BRAND = re.compile(r"learning[ _-]+the[ _-]+moving[ _-]+self", re.IGNORECASE)


def test_no_old_public_brand_variants():
    hits = []
    allowed = {ROOT / "scripts" / "verify_release.py", Path(__file__).resolve()}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path in allowed:
            continue
        if path.suffix.lower() not in {".md", ".tex", ".html", ".txt", ".cff", ".toml", ".py", ".json", ".yml", ".yaml"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if OLD_BRAND.search(text):
            hits.append(str(path.relative_to(ROOT)))
    assert not hits, "Old project branding remains in: " + ", ".join(hits)
