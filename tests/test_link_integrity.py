from pathlib import Path
import re
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]


def _markdown_targets(text: str):
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)


def test_readme_relative_links_exist():
    readme = ROOT / "README.md"
    for target in _markdown_targets(readme.read_text(encoding="utf-8")):
        target = target.strip().split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        assert (ROOT / target).exists(), f"broken README link: {target}"


class _Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.targets = []
    def handle_starttag(self, tag, attrs):
        if tag in {"a", "img", "video", "source"}:
            d = dict(attrs)
            for key in ("href", "src"):
                if key in d:
                    self.targets.append(d[key])


def test_project_page_local_links_exist():
    page = ROOT / "portfolio" / "index.html"
    parser = _Links(); parser.feed(page.read_text(encoding="utf-8"))
    for target in parser.targets:
        clean = target.split("#", 1)[0].split("?", 1)[0]
        if not clean or clean.startswith(("http://", "https://", "mailto:", "data:", "#")):
            continue
        assert (page.parent / clean).resolve().exists(), f"broken project-page asset/link: {target}"
