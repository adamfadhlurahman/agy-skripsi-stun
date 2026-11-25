"""Build zotero_map.json from Zotero Desktop Local API or an exported CSL JSON file."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import urllib.request


CSL_SCHEMA = "https://github.com/citation-style-language/schema/raw/master/csl-citation.json"


def list_collections(user_id: str) -> list[dict]:
    url = f"http://127.0.0.1:23119/api/users/{user_id}/collections?limit=200"
    with urllib.request.urlopen(urllib.request.Request(url), timeout=8) as resp:
        return json.loads(resp.read().decode("utf-8"))


def resolve_collection_by_name(user_id: str, name: str) -> str:
    cols = list_collections(user_id)
    target = name.strip().lower()
    for col in cols:
        cname = str(col.get("data", {}).get("name", "")).strip()
        if cname.lower() == target:
            return str(col.get("key", ""))
    avail = [str(c.get("data", {}).get("name", "")) for c in cols]
    raise ValueError(f"Collection {name!r} not found. Available collections: {avail}")


def fetch_from_local_api(user_id: str, collection_key: str) -> dict:
    base = f"http://127.0.0.1:23119/api/users/{user_id}"
    if collection_key:
        url = f"{base}/collections/{collection_key}/items?format=csljson&limit=500"
    else:
        url = f"{base}/items?format=csljson&limit=500"

    with urllib.request.urlopen(urllib.request.Request(url), timeout=8) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    items_map: dict[str, dict] = {}
    prefix = ""
    for item in data.get("items", []):
        uri = item.get("id", "")
        key = uri.rstrip("/").split("/")[-1] if uri else item.get("itemKey", "")
        if not key:
            continue
        if not prefix and "/" in str(uri):
            prefix = str(uri).rsplit("/", 1)[0] + "/"
        items_map[key] = item

    return {
        "collection_key": collection_key,
        "user_uri_prefix": prefix or f"http://zotero.org/users/{user_id}/items/",
        "csl_schema": CSL_SCHEMA,
        "items": items_map,
    }


def _parse_author_token(raw: str) -> dict:
    s = re.sub(r"\s+", " ", raw.strip().strip("{}")).strip()
    if not s:
        return {"literal": raw}
    if "," in s:
        fam, giv = [p.strip() for p in s.split(",", 1)]
        out = {"family": fam}
        if giv:
            out["given"] = giv
        return out
    parts = s.split()
    if len(parts) == 1:
        return {"family": parts[0]}
    return {"family": parts[-1], "given": " ".join(parts[:-1])}


def _make_ref_key(csl: dict, fallback: str, existing: set[str]) -> str:
    base = re.sub(r"[^A-Za-z0-9_-]", "", fallback) or ""
    if not base:
        auths = csl.get("author", [])
        fam = (auths[0].get("family") or auths[0].get("literal") or "REF") if auths else "REF"
        fam_clean = re.sub(r"[^A-Za-z]", "", fam).upper()[:12] or "REF"
        dp = csl.get("issued", {}).get("date-parts", [[]])
        yr = str(dp[0][0])[:4] if dp and dp[0] else "0000"
        base = f"{fam_clean}{yr}"
    key = base
    idx = 2
    while key in existing:
        key = f"{base}_{idx}"
        idx += 1
    return key


def load_from_csl_json(csl_path: pathlib.Path, user_id: str, collection_key: str, provider: str = "zotero") -> dict:
    raw = json.loads(csl_path.read_text(encoding="utf-8"))
    raw_items = raw.get("items", raw) if isinstance(raw, dict) else raw
    items_map: dict[str, dict] = {}
    prefix = f"http://zotero.org/users/{user_id}/items/"
    for item in raw_items:
        uri = str(item.get("id", ""))
        key = uri.rstrip("/").split("/")[-1] if "/" in uri else uri
        if not key:
            key = _make_ref_key(item, "", set(items_map.keys()))
        items_map[key] = item
    return {
        "provider": provider,
        "collection_key": collection_key,
        "user_uri_prefix": prefix,
        "csl_schema": CSL_SCHEMA,
        "items": items_map,
    }


def load_from_bibtex(bib_path: pathlib.Path, user_id: str, collection_key: str, provider: str = "mendeley") -> dict:
    import re as _re

    txt = bib_path.read_text(encoding="utf-8", errors="replace")
    items_map: dict[str, dict] = {}
    prefix = f"http://zotero.org/users/{user_id}/items/"

    pos = 0
    n = len(txt)
    while pos < n:
        at = txt.find("@", pos)
        if at == -1:
            break
        m_hdr = _re.match(r"@([A-Za-z]+)\s*([({])\s*([^,\s]+)\s*,", txt[at:])
        if not m_hdr:
            pos = at + 1
            continue
        etype = m_hdr.group(1).lower()
        open_ch = m_hdr.group(2)
        close_ch = "}" if open_ch == "{" else ")"
        citekey = m_hdr.group(3).strip()
        start_body = at + m_hdr.end()
        depth = 1
        i = start_body
        while i < n and depth > 0:
            if txt[i] == open_ch:
                depth += 1
            elif txt[i] == close_ch:
                depth -= 1
            i += 1
        body = txt[start_body : i - 1] if depth == 0 else txt[start_body:]
        pos = i

        if etype in ("string", "preamble", "comment"):
            continue

        fields: dict[str, str] = {}
        fi = 0
        bn = len(body)
        while fi < bn:
            while fi < bn and body[fi] in " \t\r\n,":
                fi += 1
            if fi >= bn:
                break
            km = _re.match(r"([A-Za-z0-9_-]+)\s*=\s*", body[fi:])
            if not km:
                fi += 1
                continue
            fname = km.group(1).lower()
            fi += km.end()
            if fi >= bn:
                break
            if body[fi] == "{":
                d, vj = 1, fi + 1
                while vj < bn and d > 0:
                    if body[vj] == "{":
                        d += 1
                    elif body[vj] == "}":
                        d -= 1
                    vj += 1
                val = body[fi + 1 : vj - 1]
                fi = vj
            elif body[fi] == '"':
                vj = fi + 1
                while vj < bn and not (body[vj] == '"' and body[vj - 1] != "\\"):
                    vj += 1
                val = body[fi + 1 : vj]
                fi = vj + 1
            else:
                vj = fi
                while vj < bn and body[vj] not in ",\r\n}":
                    vj += 1
                val = body[fi:vj]
                fi = vj
            val = _re.sub(r"\s+", " ", val.replace("{", "").replace("}", "")).strip()
            fields[fname] = val

        authors = [_parse_author_token(a) for a in _re.split(r"\s+and\s+", fields.get("author", "")) if a.strip()]
        yr_m = _re.search(r"(?:19|20)\d{2}", fields.get("year", ""))
        yr = int(yr_m.group(0)) if yr_m else None
        doi = _re.sub(r"^https?://(?:dx\.)?doi\.org/", "", fields.get("doi", ""), flags=_re.I).strip()
        pages = fields.get("pages", "").replace("--", "-").strip()
        journal = fields.get("journal") or fields.get("booktitle") or fields.get("publisher") or ""
        csl = {
            "type": "article-journal" if fields.get("journal") else ("chapter" if etype in ("incollection", "inproceedings") else "book" if etype == "book" else "article"),
            "title": fields.get("title", citekey),
            "container-title": journal,
            "volume": fields.get("volume", ""),
            "issue": fields.get("number", ""),
            "page": pages,
            "DOI": doi,
            "URL": fields.get("url") or (f"https://doi.org/{doi}" if doi else ""),
            "author": authors,
            "issued": {"date-parts": [[yr]]} if yr else {},
        }
        key = _make_ref_key(csl, citekey, set(items_map.keys()))
        csl["id"] = f"{prefix}{key}"
        items_map[key] = csl

    return {
        "provider": provider,
        "collection_key": collection_key,
        "user_uri_prefix": prefix,
        "csl_schema": CSL_SCHEMA,
        "items": items_map,
    }


def load_from_ris(ris_path: pathlib.Path, user_id: str, collection_key: str, provider: str = "mendeley") -> dict:
    import re as _re

    lines = ris_path.read_text(encoding="utf-8", errors="replace").splitlines()
    items_map: dict[str, dict] = {}
    prefix = f"http://zotero.org/users/{user_id}/items/"

    recs: list[dict[str, list[str]]] = []
    cur: dict[str, list[str]] = {}
    last_tag = ""
    for ln in lines:
        m = _re.match(r"^([A-Z0-9]{2})\s{1,3}-\s*(.*)$", ln)
        if m:
            tag, val = m.group(1), m.group(2).strip()
            if tag == "TY":
                cur = {"TY": [val]}
                last_tag = "TY"
            elif tag == "ER":
                if cur:
                    recs.append(cur)
                cur = {}
                last_tag = ""
            else:
                cur.setdefault(tag, []).append(val)
                last_tag = tag
        elif last_tag and ln.strip():
            cur[last_tag][-1] = f"{cur[last_tag][-1]} {ln.strip()}"
    if cur:
        recs.append(cur)

    for rec in recs:
        raw_auths = rec.get("AU") or rec.get("A1") or []
        authors = [_parse_author_token(a) for a in raw_auths if a.strip()]
        title = (rec.get("TI") or rec.get("T1") or [""])[0]
        journal = (rec.get("JO") or rec.get("T2") or rec.get("JF") or rec.get("PB") or [""])[0]
        yr_raw = (rec.get("PY") or rec.get("Y1") or [""])[0]
        yr_m = _re.search(r"(?:19|20)\d{2}", yr_raw)
        yr = int(yr_m.group(0)) if yr_m else None
        sp = (rec.get("SP") or [""])[0]
        ep = (rec.get("EP") or [""])[0]
        pages = f"{sp}-{ep}" if (sp and ep) else sp
        doi = _re.sub(r"^https?://(?:dx\.)?doi\.org/", "", (rec.get("DO") or [""])[0], flags=_re.I).strip()
        url = (rec.get("UR") or [""])[0] or (f"https://doi.org/{doi}" if doi else "")
        rtype = (rec.get("TY") or ["JOUR"])[0].upper()
        csl = {
            "type": "article-journal" if rtype in ("JOUR", "EJOUR", "MGZN") else ("book" if rtype == "BOOK" else "article"),
            "title": title,
            "container-title": journal,
            "volume": (rec.get("VL") or [""])[0],
            "issue": (rec.get("IS") or [""])[0],
            "page": pages,
            "DOI": doi,
            "URL": url,
            "author": authors,
            "issued": {"date-parts": [[yr]]} if yr else {},
        }
        key = _make_ref_key(csl, "", set(items_map.keys()))
        csl["id"] = f"{prefix}{key}"
        items_map[key] = csl

    return {
        "provider": provider,
        "collection_key": collection_key,
        "user_uri_prefix": prefix,
        "csl_schema": CSL_SCHEMA,
        "items": items_map,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build reference map (zotero_map.json) from Zotero, Mendeley (.bib/.ris), or CSL-JSON.")
    parser.add_argument("--list-collections", action="store_true", help="List available Zotero collections and keys")
    parser.add_argument("--collection", default="", help="Zotero collection key (optional)")
    parser.add_argument("--collection-name", default="", help="Zotero collection name (auto-resolves key)")
    parser.add_argument("--user-id", default="0", help="Zotero local API user id (default: 0)")
    parser.add_argument("--csl-json", type=pathlib.Path, default=None, help="Path to exported CSL-JSON file (Zotero or Mendeley)")
    parser.add_argument("--bib", type=pathlib.Path, default=None, help="Path to exported BibTeX (.bib) file (Mendeley / Zotero)")
    parser.add_argument("--ris", type=pathlib.Path, default=None, help="Path to exported RIS (.ris) file (Mendeley / Zotero)")
    parser.add_argument("--provider", choices=["auto", "zotero", "mendeley", "apa_static"], default="auto", help="Citation manager mode")
    parser.add_argument("--out", type=pathlib.Path, default=None, help="Output zotero_map.json path")
    args = parser.parse_args()

    if args.list_collections:
        cols = list_collections(args.user_id)
        print(f"Found {len(cols)} Zotero collections:")
        for c in cols:
            print(f"  {c.get('key', ''):10s} | {c.get('data', {}).get('name', '')}")
        return

    if args.out is None:
        parser.error("--out is required unless --list-collections is specified.")

    col_key = args.collection
    if args.collection_name and not col_key:
        col_key = resolve_collection_by_name(args.user_id, args.collection_name)
        print(f"Resolved collection '{args.collection_name}' -> key {col_key}")

    prov = args.provider
    if args.bib is not None:
        zmap = load_from_bibtex(args.bib, args.user_id, col_key, provider=("mendeley" if prov == "auto" else prov))
    elif args.ris is not None:
        zmap = load_from_ris(args.ris, args.user_id, col_key, provider=("mendeley" if prov == "auto" else prov))
    elif args.csl_json is not None:
        zmap = load_from_csl_json(args.csl_json, args.user_id, col_key, provider=("zotero" if prov == "auto" else prov))
    else:
        zmap = fetch_from_local_api(args.user_id, col_key)
        zmap["provider"] = "zotero" if prov == "auto" else prov

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(zmap, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: Wrote {len(zmap['items'])} {zmap.get('provider', 'zotero')} items -> {args.out}")


if __name__ == "__main__":
    main()
