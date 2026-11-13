"""Shared PDF text and metadata helpers."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader

EXAM_DATE = re.compile(
    r"Exam Date\s*&\s*Time:\s*(\d{1,2})-([A-Za-z]{3})-(\d{4})",
    re.I,
)


def pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join((p.extract_text() or "") for p in reader.pages)


def exam_date_iso(text: str) -> str:
    m = EXAM_DATE.search(text)
    if not m:
        return ""
    day, mon, year = int(m.group(1)), m.group(2), int(m.group(3))
    dt = datetime.strptime(f"{day}-{mon}-{year}", "%d-%b-%Y")
    return dt.strftime("%Y-%m-%d")


def exam_date_iso_from_pdf(path: Path) -> str:
    return exam_date_iso(pdf_text(path))
