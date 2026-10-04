from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def _relative_links(path: Path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    links = re.findall(r"\[[^\]]*\]\(([^)]+)\)", text)
    links += re.findall(r"href=[\"']([^\"']+)[\"']", text)
    for raw in links:
        link = raw.strip().split("#", 1)[0]
        if not link or link.startswith(("http://", "https://", "mailto:", "javascript:", "data:")):
            continue
        yield link


def test_all_local_markdown_and_html_links_resolve():
    missing = []
    paths = list(ROOT.rglob("*.md")) + list(ROOT.rglob("*.html"))
    for path in paths:
        # Build/cache directories are not part of the source documentation surface.
        if any(part in {".git", ".pytest_cache", "__pycache__"} for part in path.parts):
            continue
        for link in _relative_links(path):
            target = (path.parent / link).resolve()
            if not target.exists():
                missing.append(f"{path.relative_to(ROOT)} -> {link}")
    assert not missing, "Broken local links:\n" + "\n".join(missing)
