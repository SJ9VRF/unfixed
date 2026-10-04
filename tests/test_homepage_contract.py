from pathlib import Path
import re
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "portfolio" / "index.html"

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.hrefs=[]
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            d=dict(attrs)
            if "href" in d: self.hrefs.append(d["href"])

def test_project_page_contract_and_links():
    text=PAGE.read_text(encoding="utf-8")
    # Hero contract
    for required in [
        "The Unfixed User", "Aura Yavary", "Paper ↗", "Code ↗",
        "Demo ↓", "Benchmark ↗", "Video ▶",
        "Why this problem matters", "Core idea", "Architecture", "My contribution",
        "Experiments", "Results", "Failure analysis", "Interactive demo", "Scaling",
        "Safety / limitations", "Technical deep dive", "Artifacts", "Citation",
        "Agent loop", "Post-training / RL-compatible loop", "Recovery loop",
        "Success rate", "Recovery", "Latency", "Hosted API cost",
        "Permission boundary", "Inference is not authorization",
    ]:
        assert required in text, required

    # Required artifact labels from the user's project-page contract.
    for artifact in ["Paper", "Code", "Benchmark", "Dataset", "Demo", "Video", "Technical report", "Blog post"]:
        assert artifact in text

    # The project itself remains date-free. Reference years live outside this page.
    assert not re.search(r"\b20\d{2}\b", text)

    parser=Links(); parser.feed(text)
    for href in parser.hrefs:
        if href.startswith(("#", "http://", "https://", "mailto:")):
            continue
        target=(PAGE.parent / href.split("#",1)[0]).resolve()
        assert target.exists(), f"broken project-page link: {href} -> {target}"
