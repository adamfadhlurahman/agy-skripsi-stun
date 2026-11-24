"""Formal academic formatting, anti-AI prose, sentence-rhythm, and n-gram similarity auditor."""

from __future__ import annotations

import argparse
import pathlib
import re


def strip_markdown(raw_text: str) -> str:
    body = re.sub(r"^---\n.*?\n---\n+", "", raw_text, flags=re.S)
    clean = re.sub(r"`([^`]+)`", r"\1", body)
    clean = re.sub(r"\*\*([^*]+)\*\*", r"\1", clean)
    clean = re.sub(r"\*([^*]+)\*", r"\1", clean)
    return clean


def read_reference_text(path: pathlib.Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        try:
            import pymupdf

            doc = pymupdf.open(str(path))
            return "\n".join(page.get_text() for page in doc)
        except ImportError:
            from pypdf import PdfReader

            reader = PdfReader(str(path))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
    if ext == ".docx":
        from docx import Document

        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)
    return strip_markdown(path.read_text(encoding="utf-8"))


def get_ngrams(txt: str, n: int = 6) -> set[tuple[str, ...]]:
    words = re.findall(r"[a-z0-9]+", txt.lower())
    return {tuple(words[i : i + n]) for i in range(max(0, len(words) - n + 1))}


def audit_markdown(md_path: pathlib.Path, against_paths: list[pathlib.Path], is_abstract: bool = False) -> int:
    raw_text = md_path.read_text(encoding="utf-8")
    clean = strip_markdown(raw_text)

    print(f"=== MANUSCRIPT AUDIT: {md_path.name} ===")
    print("\n1. WORD COUNT SUMMARY")
    if re.search(r"(?m)^## ", clean):
        sections = re.split(r"(?m)^## ", clean)
        total_words = 0
        for sec in sections:
            lines = [l for l in sec.splitlines() if l.strip()]
            if not lines:
                continue
            header = lines[0]
            body_text = " ".join(lines[1:])
            wc = len(re.findall(r"\S+", body_text))
            total_words += wc + len(re.findall(r"\S+", header))
            print(f"  {header[:48]:48s}: {wc:5d} words")
    else:
        total_words = len(re.findall(r"\S+", clean))
    print(f"  TOTAL                                           : {total_words:5d} words")
    if is_abstract:
        status_abs = "OK (<= 250)" if total_words <= 250 else "OVER LIMIT (> 250 words per STUN standard!)"
        print(f"  ABSTRACT LIMIT CHECK                            : {status_abs}")

    print("\n2. FORMAL REGISTER & ANTI-AI REGEX CHECKS")
    checks = [
        ("Pronoun 1st/2nd person (saya/aku/kita/kami/anda)", r"\b(saya|aku|kita|kami|anda|engkau|kamu)\b", re.I),
        ("Forbidden sentence starter", r"(?:^|[.!?]\s+)(Sedangkan|Sehingga|Dan|Atau|Konsekuensinya|Dimana|Di mana)\b", 0),
        ("Forbidden di mana / yang mana / bila / di antaranya", r"\b(di\s?mana|yang mana|bila|di antaranya)\b", re.I),
        ("Deictic spatial reference (di atas / di bawah)", r"\b(di atas|di bawah)\b", re.I),
        ("Em-dash U+2014", r"\u2014", 0),
        ("En-dash outside digits", r"(?<!\d)\u2013|\u2013(?!\d)", 0),
        ("Ampersand outside parentheses", r"(?<!\()\b[A-Z][a-zA-Z'’-]+\s+&\s+[A-Z]", 0),
        ("'dan' inside parentheses citation", r"\([A-Z][A-Za-z'’-]+\s+dan\s+[A-Z][A-Za-z'’-]+,\s*\d{4}", 0),
        ("Weak verb + nominalization", r"\b(mengalami|melakukan|memberi|memberikan)\s+[a-z]+(an|si|tribusi)\b", re.I),
        ("Anticipatory negation (bukan berarti / bukan X, melainkan Y)", r"\b(?:ini|hal ini)?\s*bukan berarti\b|bukan\s+(?:sekadar\s+)?[^,.]+,\s*melainkan\b", re.I),
        ("Stray markdown backtick/asterisk/dollar", r"(`|\*|\$)", 0),
    ]

    issue_count = 0
    for label, pat, flags in checks:
        matches = list(re.finditer(pat, clean, flags))
        if label == "Ampersand outside parentheses":
            filtered = []
            for m in matches:
                open_p = clean[: m.start()].rfind("(")
                close_p = clean[: m.start()].rfind(")")
                if open_p <= close_p:
                    filtered.append((m.group(0), clean[max(0, m.start() - 25) : min(len(clean), m.end() + 25)].replace("\n", " ")))
        elif label == "Stray markdown backtick/asterisk/dollar":
            filtered = []
            eq_spans = [
                (em.start(), em.end())
                for em in re.finditer(r"(?m)^\$\$.+?\$\$\s+\(\d+\.\d+\)\s*$", clean)
            ]
            for m in matches:
                ch = m.group(0)
                if ch == "$" and (
                    clean[max(0, m.start() - 2) : m.start() + 1] == "US$"
                    or any(s0 <= m.start() < s1 for s0, s1 in eq_spans)
                ):
                    continue
                filtered.append((ch, clean[max(0, m.start() - 25) : min(len(clean), m.end() + 25)].replace("\n", " ")))
        else:
            filtered = [(m.group(0), clean[max(0, m.start() - 25) : min(len(clean), m.end() + 25)].replace("\n", " ")) for m in matches]

        if filtered:
            issue_count += len(filtered)
        print(f"  [{len(filtered):2d}] {label}")
        for g, c in filtered[:5]:
            print(f"       -> {g!r} in ...{c}...")

    print("\n3. SENTENCE LENGTH PROFILE")
    prose_lines = [l for l in clean.splitlines() if l.strip() and not l.startswith("#") and not l.startswith("|")]
    prose = "\n".join(prose_lines)
    prot = re.sub(r"\b(No|p|pp|hlm|al|et|dkk|Corp|Ltd|Inc|PT|dll)\.", r"\1<DOT>", prose)
    prot = re.sub(r"(\d)\.(\d)", r"\1<DOT>\2", prot)
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", prot) if len(re.findall(r"\S+", s)) > 3]
    lengths = [len(re.findall(r"\S+", s.replace("<DOT>", "."))) for s in sents]
    long_sents = [(i, w, sents[i - 1].replace("<DOT>", ".")[:95]) for i, w in enumerate(lengths, 1) if w >= 28]
    if lengths:
        mean_l = sum(lengths) / len(lengths)
        var_l = sum((x - mean_l) ** 2 for x in lengths) / len(lengths)
        sd_l = var_l ** 0.5
        print(f"  Sentences >=4w: {len(lengths)} | Mean: {mean_l:.1f}w | SD: {sd_l:.1f}w | >=28w: {len(long_sents)} ({100*len(long_sents)/len(lengths):.1f}%)")
        for i, w, prev in long_sents[:10]:
            print(f"    S{i:03d} ({w:2d}w): {prev}...")
    else:
        print("  No prose sentences found.")

    if against_paths:
        print("\n4. N-GRAM OVERLAP CHECK")
        src_6g = get_ngrams(clean, 6)
        src_7g = get_ngrams(clean, 7)
        for ref_path in against_paths:
            if not ref_path.exists():
                print(f"  [SKIP] Missing reference: {ref_path}")
                continue
            ref_txt = read_reference_text(ref_path)
            ov6 = sorted(" ".join(g) for g in (src_6g & get_ngrams(ref_txt, 6)))
            ov7 = sorted(" ".join(g) for g in (src_7g & get_ngrams(ref_txt, 7)))
            print(f"  vs {ref_path.name}: {len(ov6)} shared 6-grams, {len(ov7)} shared 7-grams")
            for g in ov6[:8]:
                print(f"      6g: {g}")

    return issue_count


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit Markdown chapter against STUN formal prose, anti-AI, and n-gram checks.")
    parser.add_argument("markdown", type=pathlib.Path, help="Path to Markdown chapter file")
    parser.add_argument("--against", type=pathlib.Path, nargs="*", default=[], help="Reference files (.pdf/.docx/.md) for n-gram check")
    parser.add_argument("--abstract", action="store_true", help="Check <= 250 word limit for Abstract")
    args = parser.parse_args()
    audit_markdown(args.markdown, args.against, is_abstract=args.abstract)


if __name__ == "__main__":
    main()
