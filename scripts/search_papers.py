"""Built-in academic paper finder & legal Open-Access PDF downloader (OpenAlex + CrossRef).

Works out of the box with Python's standard library (zero API keys, zero MCP servers required).
Supports keyword search, DOI lookup, reconstructing abstracts, downloading legal Open-Access PDFs
into `01. Literature/`, and exporting verified CSL-JSON entries into `03. Drafts/zotero_map.json`.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

UA = "AGY-Thesis-StarterKit/1.0 (Academic Research Client; mailto:support@example.org)"
CSL_SCHEMA = "https://github.com/citation-style-language/schema/raw/master/csl-citation.json"


def _http_json(url: str, timeout: int = 18) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def _reconstruct_abstract(inv_idx: dict | None) -> str:
    if not isinstance(inv_idx, dict) or not inv_idx:
        return ""
    max_pos = 0
    for positions in inv_idx.values():
        if positions:
            max_pos = max(max_pos, max(positions))
    words = [""] * (max_pos + 1)
    for word, positions in inv_idx.items():
        for pos in positions:
            if 0 <= pos < len(words):
                words[pos] = word
    return re.sub(r"\s+", " ", " ".join(w for w in words if w)).strip()


def _split_author_name(full_name: str) -> dict:
    parts = [p for p in full_name.strip().split() if p]
    if not parts:
        return {"literal": full_name}
    if len(parts) == 1:
        return {"family": parts[0]}
    return {"family": parts[-1], "given": " ".join(parts[:-1])}


def _clean_doi(raw: str | None) -> str:
    if not raw:
        return ""
    s = raw.strip()
    s = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", s, flags=re.I)
    return s.strip()


def _make_item_key(csl_item: dict, existing: set[str]) -> str:
    authors = csl_item.get("author", [])
    fam = ""
    if authors:
        fam = authors[0].get("family") or authors[0].get("literal") or ""
    nfkd = unicodedata.normalize("NFKD", fam)
    ascii_fam = re.sub(r"[^A-Za-z]", "", "".join(c for c in nfkd if not unicodedata.combining(c))).upper()
    if not ascii_fam:
        ascii_fam = "REF"
    yr = ""
    dp = csl_item.get("issued", {}).get("date-parts", [[]])
    if dp and dp[0]:
        yr = str(dp[0][0])[:4]
    base = f"{ascii_fam[:12]}{yr or '0000'}"
    key = base
    idx = 2
    while key in existing:
        key = f"{base}_{idx}"
        idx += 1
    return key


def _safe_filename(name: str, max_len: int = 85) -> str:
    cleaned = re.sub(r'[\\/:*?"<>|\r\n\t]+', " ", name)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    return cleaned[:max_len].strip(" .")


def fetch_crossref_doi(doi: str) -> dict | None:
    clean = _clean_doi(doi)
    if not clean:
        return None
    url = f"https://api.crossref.org/works/{urllib.parse.quote(clean, safe='/')}"
    data = _http_json(url)
    msg = data.get("message", {})
    if not msg:
        return None

    authors = []
    for a in msg.get("author", []):
        fam = a.get("family")
        giv = a.get("given")
        if fam:
            entry = {"family": fam}
            if giv:
                entry["given"] = giv
            authors.append(entry)
        elif a.get("name"):
            authors.append({"literal": a["name"]})

    yr = None
    for k in ("published-print", "published-online", "issued", "created"):
        dp = msg.get(k, {}).get("date-parts", [[]])
        if dp and dp[0] and dp[0][0]:
            yr = int(dp[0][0])
            break

    title = (msg.get("title") or [""])[0]
    journal = (msg.get("container-title") or [""])[0]
    abstract = re.sub(r"<[^>]+>", " ", msg.get("abstract") or "")
    abstract = re.sub(r"\s+", " ", abstract).strip()

    csl = {
        "type": "article-journal" if journal else "article",
        "title": title,
        "container-title": journal,
        "volume": str(msg.get("volume") or ""),
        "issue": str(msg.get("issue") or ""),
        "page": str(msg.get("page") or ""),
        "DOI": clean,
        "URL": f"https://doi.org/{clean}",
        "author": authors,
        "issued": {"date-parts": [[yr]]} if yr else {},
    }
    return {
        "source": "crossref",
        "title": title,
        "year": yr or "",
        "authors": [
            f"{a.get('given', '')} {a.get('family', a.get('literal', ''))}".strip()
            for a in authors
        ],
        "journal": journal,
        "doi": clean,
        "citations": msg.get("is-referenced-by-count", 0),
        "is_oa": False,
        "pdf_url": "",
        "abstract": abstract,
        "csl": csl,
    }


def search_openalex(query: str, limit: int = 8, year_from: int | None = None, year_to: int | None = None, oa_only: bool = False) -> list[dict]:
    params = {
        "search": query,
        "per-page": str(min(max(limit, 1), 25)),
        "sort": "relevance_score:desc",
    }
    filters = []
    if year_from and year_to:
        filters.append(f"publication_year:{year_from}-{year_to}")
    elif year_from:
        filters.append(f"publication_year:>={year_from}")
    elif year_to:
        filters.append(f"publication_year:<={year_to}")
    if oa_only:
        filters.append("is_oa:true")
    if filters:
        params["filter"] = ",".join(filters)

    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    data = _http_json(url)
    results = []
    for w in data.get("results", []):
        title = (w.get("title") or "").strip()
        yr = w.get("publication_year") or ""
        doi = _clean_doi(w.get("doi"))
        authors_raw = [
            au.get("author", {}).get("display_name", "")
            for au in w.get("authorships", [])
            if au.get("author", {}).get("display_name")
        ]
        loc = w.get("best_oa_location") or w.get("primary_location") or {}
        src = (w.get("primary_location") or {}).get("source") or {}
        journal = src.get("display_name") or (loc.get("source") or {}).get("display_name") or ""
        biblio = w.get("biblio") or {}
        pdf_url = loc.get("pdf_url") or ""
        oa_info = w.get("open_access") or {}
        is_oa = bool(oa_info.get("is_oa"))
        if not pdf_url and oa_info.get("oa_url", "").lower().endswith(".pdf"):
            pdf_url = oa_info["oa_url"]

        pages = ""
        if biblio.get("first_page"):
            pages = f"{biblio['first_page']}-{biblio['last_page']}" if biblio.get("last_page") else str(biblio["first_page"])

        csl = {
            "type": "article-journal" if journal else "article",
            "title": title,
            "container-title": journal,
            "volume": str(biblio.get("volume") or ""),
            "issue": str(biblio.get("issue") or ""),
            "page": pages,
            "DOI": doi,
            "URL": f"https://doi.org/{doi}" if doi else (w.get("id") or ""),
            "author": [_split_author_name(a) for a in authors_raw],
            "issued": {"date-parts": [[int(yr)]]} if yr else {},
        }
        results.append(
            {
                "source": "openalex",
                "title": title,
                "year": yr,
                "authors": authors_raw,
                "journal": journal,
                "doi": doi,
                "citations": w.get("cited_by_count", 0),
                "is_oa": is_oa,
                "pdf_url": pdf_url,
                "abstract": _reconstruct_abstract(w.get("abstract_inverted_index")),
                "csl": csl,
            }
        )
    return results


def search_crossref(query: str, limit: int = 8, year_from: int | None = None) -> list[dict]:
    params = {"query": query, "rows": str(min(max(limit, 1), 20))}
    if year_from:
        params["filter"] = f"from-pub-date:{year_from}"
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
    data = _http_json(url)
    out = []
    for msg in data.get("message", {}).get("items", []):
        doi = _clean_doi(msg.get("DOI"))
        authors = []
        authors_raw = []
        for a in msg.get("author", []):
            fam = a.get("family")
            giv = a.get("given")
            if fam:
                entry = {"family": fam}
                if giv:
                    entry["given"] = giv
                authors.append(entry)
                authors_raw.append(f"{giv or ''} {fam}".strip())
        yr = ""
        dp = msg.get("issued", {}).get("date-parts", [[]])
        if dp and dp[0] and dp[0][0]:
            yr = int(dp[0][0])
        title = (msg.get("title") or [""])[0]
        journal = (msg.get("container-title") or [""])[0]
        csl = {
            "type": "article-journal" if journal else "article",
            "title": title,
            "container-title": journal,
            "volume": str(msg.get("volume") or ""),
            "issue": str(msg.get("issue") or ""),
            "page": str(msg.get("page") or ""),
            "DOI": doi,
            "URL": f"https://doi.org/{doi}" if doi else "",
            "author": authors,
            "issued": {"date-parts": [[yr]]} if yr else {},
        }
        out.append(
            {
                "source": "crossref",
                "title": title,
                "year": yr,
                "authors": authors_raw,
                "journal": journal,
                "doi": doi,
                "citations": msg.get("is-referenced-by-count", 0),
                "is_oa": False,
                "pdf_url": "",
                "abstract": "",
                "csl": csl,
            }
        )
    return out


def download_oa_pdf(paper: dict, out_dir: pathlib.Path) -> pathlib.Path | None:
    pdf_url = paper.get("pdf_url") or ""
    if not pdf_url:
        return None
    out_dir.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(pdf_url, headers={"User-Agent": UA, "Accept": "application/pdf"})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            ctype = resp.headers.get("Content-Type", "").lower()
            blob = resp.read(15 * 1024 * 1024)
            if not (blob.startswith(b"%PDF-") or "pdf" in ctype):
                return None
    except Exception:
        return None

    first_auth = "Unknown"
    if paper.get("authors"):
        first_auth = paper["authors"][0].split()[-1]
    yr = str(paper.get("year") or "n.d.")
    short_t = _safe_filename(paper.get("title", "Paper"), max_len=60)
    fname = _safe_filename(f"{first_auth} ({yr}) - {short_t}", max_len=100) + ".pdf"
    target = out_dir / fname
    target.write_bytes(blob)
    return target


def export_to_zotero_map(papers: list[dict], map_path: pathlib.Path, enrich_crossref: bool = True) -> int:
    if map_path.exists():
        zmap = json.loads(map_path.read_text(encoding="utf-8"))
    else:
        zmap = {
            "collection_key": "",
            "user_uri_prefix": "http://zotero.org/users/0/items/",
            "csl_schema": CSL_SCHEMA,
            "items": {},
        }
    items = zmap.setdefault("items", {})
    prefix = zmap.get("user_uri_prefix", "http://zotero.org/users/0/items/")
    existing_dois = {_clean_doi(v.get("DOI")).lower(): k for k, v in items.items() if v.get("DOI")}

    added = 0
    for p in papers:
        csl = dict(p.get("csl") or {})
        doi = _clean_doi(csl.get("DOI") or p.get("doi"))
        if enrich_crossref and doi and (not csl.get("page") or not csl.get("volume")):
            try:
                cr = fetch_crossref_doi(doi)
                if cr and cr.get("csl"):
                    csl = cr["csl"]
            except Exception:
                pass
        if doi and doi.lower() in existing_dois:
            continue
        key = _make_item_key(csl, set(items.keys()))
        csl["id"] = f"{prefix}{key}"
        items[key] = csl
        if doi:
            existing_dois[doi.lower()] = key
        added += 1

    map_path.parent.mkdir(parents=True, exist_ok=True)
    map_path.write_text(json.dumps(zmap, ensure_ascii=False, indent=2), encoding="utf-8")
    return added


def main() -> None:
    parser = argparse.ArgumentParser(description="Search real academic papers via OpenAlex & CrossRef (zero MCP needed).")
    parser.add_argument("query_pos", nargs="?", default="", help="Search keywords (e.g., 'tax revenue determinants ASEAN')")
    parser.add_argument("--query", "-q", dest="query_flag", default="", help="Search keywords (alternative flag)")
    parser.add_argument("--doi", default="", help="Look up a single exact DOI via CrossRef")
    parser.add_argument("--limit", type=int, default=8, help="Number of results (default: 8, max: 25)")
    parser.add_argument("--year-from", "--from-year", dest="year_from", type=int, default=None, help="Filter minimum publication year")
    parser.add_argument("--year-to", "--to-year", dest="year_to", type=int, default=None, help="Filter maximum publication year")
    parser.add_argument("--oa-only", action="store_true", help="Restrict OpenAlex search to Open Access works")
    parser.add_argument("--source", choices=["auto", "openalex", "crossref"], default="auto", help="API source")
    parser.add_argument("--download", "--download-oa", dest="download", nargs="?", const="01. Literature", default=None, help="Download legal OA PDFs to folder")
    parser.add_argument("--export-zotero-map", "--export-zotero", dest="export_zotero_map", type=pathlib.Path, default=None, help="Merge CSL-JSON results into zotero_map.json")
    parser.add_argument("--json", action="store_true", help="Print full JSON results")
    args = parser.parse_args()
    args.query = (args.query_flag or args.query_pos or "").strip()

    if not args.query and not args.doi:
        parser.error("Provide either a search query or --doi.")

    papers: list[dict] = []
    if args.doi:
        item = fetch_crossref_doi(args.doi)
        if item:
            papers = [item]
    else:
        if args.source in ("auto", "openalex"):
            try:
                papers = search_openalex(args.query, limit=args.limit, year_from=args.year_from, year_to=args.year_to, oa_only=args.oa_only)
            except urllib.error.URLError as e:
                if args.source == "openalex":
                    raise SystemExit(f"OpenAlex request failed: {e}") from e
        if (not papers and args.source == "auto") or args.source == "crossref":
            papers = search_crossref(args.query, limit=args.limit, year_from=args.year_from)

    downloaded: list[str] = []
    if args.download:
        dl_dir = pathlib.Path(args.download)
        for p in papers:
            saved = download_oa_pdf(p, dl_dir)
            if saved:
                p["downloaded_pdf"] = str(saved)
                downloaded.append(str(saved))

    added_zot = 0
    if args.export_zotero_map and papers:
        added_zot = export_to_zotero_map(papers, args.export_zotero_map)

    if args.json:
        print(json.dumps(papers, ensure_ascii=False, indent=2))
        return

    print(f"Found {len(papers)} paper(s):")
    for idx, p in enumerate(papers, 1):
        auths = ", ".join(p["authors"][:3]) + (" et al." if len(p["authors"]) > 3 else "")
        print(f"\n[{idx}] {p['title']} ({p['year']})")
        print(f"    Authors  : {auths or '-'}")
        print(f"    Journal  : {p['journal'] or '-'} | Citations: {p['citations']} | OA: {p['is_oa']}")
        print(f"    DOI      : {p['doi'] or '-'}")
        if p.get("pdf_url"):
            print(f"    PDF URL  : {p['pdf_url']}")
        if p.get("downloaded_pdf"):
            print(f"    Saved    : {p['downloaded_pdf']}")
        if p.get("abstract"):
            print(f"    Abstract : {p['abstract'][:260]}{'...' if len(p['abstract']) > 260 else ''}")

    if args.download:
        print(f"\nDownloaded {len(downloaded)} Open-Access PDF(s) to {args.download}.")
    if args.export_zotero_map:
        print(f"Merged {added_zot} new reference(s) into {args.export_zotero_map}.")


if __name__ == "__main__":
    main()
