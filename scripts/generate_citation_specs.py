"""Auto-generate 03. Drafts/citation_specs.json by matching in-text APA 7th citations against zotero_map.json."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import unicodedata


def norm_name(s: str) -> str:
    nfkd = unicodedata.normalize("NFKD", s or "")
    ascii_s = "".join(ch for ch in nfkd if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9\s]", " ", ascii_s.lower()).strip()


def extract_item_year(item: dict) -> str:
    issued = item.get("issued", {})
    dp = issued.get("date-parts")
    if isinstance(dp, list) and dp and isinstance(dp[0], list) and dp[0]:
        return str(dp[0][0])[:4]
    for k in ("literal", "raw"):
        if issued.get(k):
            m = re.search(r"(?:19|20)\d{2}", str(issued[k]))
            if m:
                return m.group(0)
    return ""


def extract_author_names(item: dict) -> list[str]:
    names: list[str] = []
    for a in item.get("author", []):
        fam = a.get("family") or a.get("literal") or ""
        if fam:
            names.append(norm_name(fam))
    return names


def match_author_year(author_str: str, year: str, zitems: dict[str, dict]) -> str | None:
    clean_a = re.sub(r"\b(?:dkk|et\s+al)\b\.?", "", author_str, flags=re.I)
    parts = [norm_name(p) for p in re.split(r"\s*(?:,|&|\bdan\b|\band\b)\s*", clean_a) if norm_name(p)]
    if not parts:
        return None
    first_tok = parts[0].split()[-1] if parts[0].split() else ""
    candidates: list[tuple[int, str]] = []

    for key, item in zitems.items():
        iy = extract_item_year(item)
        if iy != year:
            continue
        iauthors = extract_author_names(item)
        if not iauthors:
            title_norm = norm_name(item.get("title", ""))
            if parts[0] and parts[0] in title_norm:
                candidates.append((1, key))
            continue
        first_fam = iauthors[0]
        score = 0
        if parts[0] == first_fam:
            score += 5
        elif first_tok and first_tok in first_fam.split():
            score += 3
        elif all(tok in first_fam for tok in parts[0].split()):
            score += 2
        if score > 0 and len(parts) > 1 and len(iauthors) > 1:
            second_tok = parts[1].split()[-1] if parts[1].split() else ""
            if parts[1] == iauthors[1] or (second_tok and second_tok in iauthors[1].split()):
                score += 3
        if score > 0:
            candidates.append((score, key))

    if not candidates:
        return None
    candidates.sort(key=lambda x: -x[0])
    return candidates[0][1]


def parse_locator(loc_raw: str | None) -> tuple[str, str]:
    if not loc_raw:
        return "", "page"
    cleaned = re.sub(r"^(?:hlm\.|pp?\.|halaman)\s*", "", loc_raw.strip(), flags=re.I)
    return cleaned.strip(), "page"


def generate_specs_from_texts(texts: list[str], zmap: dict) -> tuple[list, list[str]]:
    zitems = zmap.get("items", {})
    if not zitems:
        return [], []

    joined = "\n".join(texts)
    specs_map: dict[str, list] = {}
    unmatched: set[str] = set()

    # 1. Parenthetical citations: (Author, 2024) or (A, 2020; B & C, 2021, hlm. 5)
    paren_re = re.compile(r"\(([^()\n]{3,180}?\b(?:19|20)\d{2}[a-z]?(?:,\s*(?:hlm\.|pp?\.|halaman)\s*[\d\u2013-]+)?[^()\n]*)\)")
    for m in paren_re.finditer(joined):
        full = m.group(0)
        inner = m.group(1)
        if full in specs_map:
            continue
        chunks = [c.strip() for c in inner.split(";") if c.strip()]
        item_tuples = []
        ok_all = True
        for ch in chunks:
            cm = re.match(r"^(.+?),\s*((?:19|20)\d{2})[a-z]?(?:,\s*((?:hlm\.|pp?\.|halaman)\s*[\d\u2013-]+))?$", ch, re.I)
            if not cm:
                ok_all = False
                break
            auth, yr, loc_raw = cm.groups()
            key = match_author_year(auth, yr, zitems)
            if not key:
                ok_all = False
                break
            loc, lbl = parse_locator(loc_raw)
            item_tuples.append([key, loc, lbl, False])
        if ok_all and item_tuples:
            specs_map[full] = [full, item_tuples]
        elif re.search(r"[A-Za-z]{2,},\s*(?:19|20)\d{2}", inner):
            unmatched.add(full)

    # 2. Narrative citations: Author (2024), Author dan Co (2024), Author dkk. (2024, hlm. 12)
    narr_re = re.compile(
        r"\b([A-Z][A-Za-zÀ-ÿ'’.-]+(?:\s+[A-Z][A-Za-zÀ-ÿ'’.-]+){0,3}"
        r"(?:\s+(?:dan|and)\s+[A-Z][A-Za-zÀ-ÿ'’.-]+|\s+(?:dkk\.|et\s+al\.))?)"
        r"\s+(\(((?:19|20)\d{2})[a-z]?(?:,\s*((?:hlm\.|pp?\.|halaman)\s*[\d\u2013-]+))?\))"
    )
    for m in narr_re.finditer(joined):
        full = m.group(0)
        if full in specs_map:
            continue
        auth, paren_yr, yr, loc_raw = m.groups()
        key = match_author_year(auth, yr, zitems)
        if key:
            loc, lbl = parse_locator(loc_raw)
            specs_map[full] = [full, [[key, loc, lbl, True]], f"{auth} ", paren_yr]
        else:
            unmatched.add(full)

    specs_list = [specs_map[k] for k in sorted(specs_map, key=lambda x: (-len(x), x))]
    return specs_list, sorted(unmatched)


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto-generate citation_specs.json from Markdown drafts and zotero_map.json.")
    parser.add_argument("--config", type=pathlib.Path, required=True, help="Path to thesis_config.json")
    args = parser.parse_args()

    cfg_path = args.config.resolve()
    ws_root = cfg_path.parent
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    zmap_path = ws_root / cfg["zotero"]["map_file"]
    if not zmap_path.exists():
        raise FileNotFoundError(f"zotero_map.json not found at {zmap_path}. Run scripts/build_zotero_map.py first.")
    zmap = json.loads(zmap_path.read_text(encoding="utf-8"))

    texts: list[str] = []
    for key_list in ("chapters", "proposal_appendices", "appendices"):
        for entry in cfg["paths"].get(key_list, []):
            p = ws_root / entry.get("md", "")
            if p.exists():
                texts.append(p.read_text(encoding="utf-8"))

    specs, unmatched = generate_specs_from_texts(texts, zmap)
    out_path = ws_root / cfg["zotero"]["citation_specs_file"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(specs, ensure_ascii=False, indent=2), encoding="utf-8")

    uniq_keys = sorted({tup[0] for sp in specs for tup in sp[1]})
    print(f"OK: Matched {len(specs)} citation patterns ({len(uniq_keys)} unique Zotero items) -> {out_path}")
    if unmatched:
        print(f"[WARN] Unmatched citations ({len(unmatched)}):")
        for u in unmatched[:15]:
            print(f"       - {u}")


if __name__ == "__main__":
    main()
