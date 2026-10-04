#!/usr/bin/env python3
"""Read-only verifier for an extracted release tree.

Unlike the research check, this script must not rewrite benchmark or result files.
It verifies manifest integrity, public/anonymous paper presence, author metadata,
and release hygiene.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANNED_PARTS = {"__pycache__", ".pytest_cache", ".git", "pdf_render"}
BANNED_NAMES = {".coverage"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pdfinfo(path: Path) -> str:
    try:
        return subprocess.check_output(["pdfinfo", str(path)], text=True, stderr=subprocess.STDOUT)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        return str(e)


def main() -> None:
    errors: list[str] = []
    manifest_path = ROOT / "MANIFEST.json"
    if not manifest_path.exists():
        errors.append("MANIFEST.json missing")
    else:
        manifest = json.loads(manifest_path.read_text())
        for entry in manifest.get("files", []):
            p = ROOT / entry["path"]
            if not p.is_file():
                errors.append(f"missing tracked file: {entry['path']}")
                continue
            actual = sha256(p)
            if actual != entry["sha256"]:
                errors.append(f"hash mismatch: {entry['path']}")
            if p.stat().st_size != entry["bytes"]:
                errors.append(f"size mismatch: {entry['path']}")

    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT)
        if any(part in BANNED_PARTS for part in rel.parts) or p.name in BANNED_NAMES:
            errors.append(f"release hygiene violation: {rel}")

    public_pdf = ROOT / "paper" / "the_unfixed_user.pdf"
    anon_pdf = ROOT / "paper" / "the_unfixed_user_anonymous.pdf"
    for p in (public_pdf, anon_pdf):
        if not p.is_file() or p.stat().st_size == 0:
            errors.append(f"paper missing or empty: {p.relative_to(ROOT)}")

    if public_pdf.exists():
        info = pdfinfo(public_pdf)
        if "Aura Yavary" not in info:
            errors.append("public PDF author metadata is not Aura Yavary")
        if re.search(r"CreationDate|ModDate", info):
            errors.append("public PDF contains project/build date metadata")
    if anon_pdf.exists():
        info = pdfinfo(anon_pdf)
        if "Anonymous Authors" not in info:
            errors.append("anonymous PDF metadata is not anonymous")
        if re.search(r"CreationDate|ModDate", info):
            errors.append("anonymous PDF contains project/build date metadata")

    # Public-facing text should not regress to old branding or private-name variants.
    text_exts = {".md", ".tex", ".html", ".txt", ".cff", ".toml", ".py", ".json", ".yml", ".yaml"}
    old_brand_hits = []
    old_name_hits = []
    for p in ROOT.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in text_exts:
            continue
        if p.resolve() == Path(__file__).resolve():
            continue
        try:
            txt = p.read_text(errors="ignore")
        except OSError:
            continue
        if re.search(r"learning[ _-]+the[ _-]+moving[ _-]+self", txt, flags=re.IGNORECASE):
            old_brand_hits.append(str(p.relative_to(ROOT)))
        if "Arefeh Yavary" in txt:
            old_name_hits.append(str(p.relative_to(ROOT)))
    if old_brand_hits:
        errors.append("old project branding remains in: " + ", ".join(old_brand_hits[:10]))
    if old_name_hits:
        errors.append("old public author name remains in: " + ", ".join(old_name_hits[:10]))

    out = {
        "artifact": "The Unfixed User",
        "author": "Aura Yavary",
        "ok": not errors,
        "errors": errors,
    }
    print(json.dumps(out, indent=2))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
