"""Extract clean narrative prose from a student's own PDF or DOCX for author-voice calibration."""

from __future__ import annotations

import argparse
import pathlib
import re


def extract_pdf_text(path: pathlib.Path, start_page: int = 1, end_page: int | None = None) -> str:
    try:
        import pymupdf

        doc = pymupdf.open(str(path))
        total = len(doc)
        stop = min(end_page or total, total)
        pages = [doc[i].get_text("text") for i in range(max(0, start_page - 1), stop)]
        return "\n\n".join(pages)
    except ImportError:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        total = len(reader.pages)
        stop = min(end_page or total, total)
        pages = [reader.pages[i].extract_text() or "" for i in range(max(0, start_page - 1), stop)]
        return "\n\n".join(pages)


def extract_docx_text(path: pathlib.Path) -> str:
    from docx import Document

    doc = Document(str(path))
    return "\n\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())


def clean_to_prose(raw_text: str) -> str:
    lines = raw_text.splitlines()
    paras: list[str] = []
    buf: list[str] = []

    for line in lines:
        s = line.strip()
        if not s:
            if buf:
                paras.append(" ".join(buf))
                buf = []
            continue
        if re.fullmatch(r"(?:\d{1,3}|[ivxlcdm]{1,6})", s, re.I):
            continue
        if re.match(r"^(?:Tabel|Table|Gambar|Figure|Sumber\s*:|Source\s*:|Catatan\s*:|Note\s*:)\b", s, re.I):
            continue
        if re.match(r"^(?:BAB\s+[IVX]+|CHAPTER\s+[IVX]+|\d+\.\d+(?:\.\d+)*\s+)", s, re.I):
            if buf:
                paras.append(" ".join(buf))
                buf = []
            continue
        buf.append(s)
        if len(s) < 55 and re.search(r"[.?!\"”)]$", s):
            paras.append(" ".join(buf))
            buf = []

    if buf:
        paras.append(" ".join(buf))

    cleaned: list[str] = []
    for p in paras:
        p = re.sub(r"\s+", " ", p).strip()
        p = re.sub(r"([a-zA-Z])\s+-\s*([a-zA-Z])", r"\1-\2", p)
        p = re.sub(r"([a-zA-Z])-\s+([a-zA-Z])", r"\1-\2", p)
        words = p.split()
        if len(words) < 12:
            continue
        if re.search(r"\b(?:nggak|gitu loh|sih|dong|kayak|memangnya|soalnya)\b", p, re.I):
            continue
        cleaned.append(p)

    return "\n\n".join(cleaned)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract clean prose sample from PDF/DOCX for voice profiling.")
    parser.add_argument("input", type=pathlib.Path, help="Path to PDF or DOCX of the student's own writing sample")
    parser.add_argument("--out", type=pathlib.Path, required=True, help="Output Markdown file (.md)")
    parser.add_argument("--start-page", type=int, default=1, help="Start PDF page (1-indexed)")
    parser.add_argument("--end-page", type=int, default=None, help="End PDF page (1-indexed)")
    args = parser.parse_args()

    ext = args.input.suffix.lower()
    if ext == ".pdf":
        raw = extract_pdf_text(args.input, args.start_page, args.end_page)
    elif ext == ".docx":
        raw = extract_docx_text(args.input)
    else:
        raw = args.input.read_text(encoding="utf-8")

    prose = clean_to_prose(raw)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(prose + "\n", encoding="utf-8")
    wc = len(prose.split())
    print(f"OK: Extracted {wc} prose words -> {args.out}")


if __name__ == "__main__":
    main()
