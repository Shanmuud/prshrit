#!/usr/bin/env python3
"""Download past-paper PDFs from a paper.shrit.in subject page."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

import requests

from pdfutil import exam_date_iso_from_pdf

BASE = "https://paper.shrit.in"
DATA_DIR = Path(__file__).resolve().parent / "data"
PDF_DIR = DATA_DIR / "pdfs"

QNO_LINE = re.compile(r"^(\d+[A-Z])\)\s*$")
HREF_BLOCK = re.compile(
    r'\\"href\\":\\"(/authoritative/[^\\]+\.pdf)\\"[^}]{0,400}\\"name\\":\\"([^\\]+)\\"[^}]{0,200}\\"editableId\\":\\"([a-f0-9]+)\\"',
    re.DOTALL,
)
DISPLAY_IN_FLIGHT = re.compile(
    r'\\"children\\":\\"((?:CSS|CSE)\s*\d{4})\s*·\s*(\d{1,2}\s+\w+\s+\d{4})\\"'
)
EXAM_BADGE = re.compile(
    r'\\"children\\":\\"(Makeup|End-sem|Mid-sem|Quiz|CAT)\\"',
)


def fetch_html(url: str) -> str:
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.text


def parse_subject_title(html: str) -> str:
    m = re.search(
        r'className":"mt-3 text-\[1\.45rem\][^"]*","children":"([^"]+)"', html
    )
    if m:
        return m.group(1)
    m = re.search(r"<h1[^>]*>([^<]+)</h1>", html)
    return m.group(1).strip() if m else "Unknown"


def parse_papers(html: str) -> list[dict]:
    """Parse paper list from Next.js flight payload embedded in HTML."""
    blocks = list(HREF_BLOCK.finditer(html))
    if not blocks:
        raise RuntimeError("No /authoritative/*.pdf links found in page HTML")

    badges = EXAM_BADGE.findall(html)
    badge_iter = iter(badges)
    display_rows = DISPLAY_IN_FLIGHT.findall(html.replace("\\u00b7", "·"))
    display_iter = iter(display_rows)

    papers: list[dict] = []
    seen_paths: set[str] = set()

    for m in blocks:
        path = m.group(1)
        if path in seen_paths:
            continue
        seen_paths.add(path)

        archive_name = m.group(2)
        paper_id = m.group(3)
        start = max(0, m.start() - 2500)
        window = html[start : m.end() + 3500]

        code = ""
        date = ""
        try:
            code, date = next(display_iter)
            code = code.strip()
            date = date.strip()
        except StopIteration:
            code = guess_code(path, archive_name)
            date = ""

        exam_type = next(badge_iter, "")
        if not exam_type:
            if "Makeup" in archive_name or "Makeup" in path:
                exam_type = "Makeup"
            elif "Regular" in archive_name or "END" in archive_name.upper():
                exam_type = "End-sem"
            else:
                exam_type = "Unknown"

        filename = safe_filename(path, paper_id)
        papers.append(
            {
                "id": paper_id,
                "code": code or guess_code(path, archive_name),
                "title": parse_subject_title(html),
                "date": date,
                "exam_type": exam_type,
                "url": urljoin(BASE, path),
                "file": str(PDF_DIR / filename),
                "archive_name": archive_name,
            }
        )

    return papers


def guess_code(path: str, archive_name: str) -> str:
    for src in (path, archive_name):
        m = re.search(r"(CSS[_\s-]?\d{4}|CSE[_\s-]?\d{4})", src, re.I)
        if m:
            return m.group(1).replace("_", " ").replace("-", " ").upper()
    return ""


def safe_filename(path: str, paper_id: str) -> str:
    tail = unquote(path.split("/")[-1])
    stem = re.sub(r"[^\w.\-]+", "_", tail)
    if not stem.lower().endswith(".pdf"):
        stem += ".pdf"
    return f"{paper_id}_{stem}"


def download_pdf(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    dest.write_bytes(r.content)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Subject page URL on paper.shrit.in")
    parser.add_argument(
        "-o",
        "--output",
        default=str(DATA_DIR / "papers.json"),
        help="Output papers manifest (default: data/papers.json)",
    )
    args = parser.parse_args(argv)

    html = fetch_html(args.url)
    papers = parse_papers(html)

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    for p in papers:
        dest = Path(p["file"])
        download_pdf(p["url"], dest)
        iso = exam_date_iso_from_pdf(dest)
        if iso:
            p["date"] = iso
        print(f"Downloaded {p['code']} {p['date']} -> {dest.name}")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    for p in papers:
        p.pop("archive_name", None)
    out.write_text(json.dumps(papers, indent=2), encoding="utf-8")
    print(f"Wrote {len(papers)} papers to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
