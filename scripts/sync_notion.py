"""Zero-MCP Notion REST API bridge for the bundled Purple Notion Research Dashboard.

Uses only Python's standard library (`urllib.request`, `json`, `os`, `re`, `pathlib`)
and reads `NOTION_TOKEN` from `.env` or environment variables.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import urllib.error
import urllib.request

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def load_token(ws_root: pathlib.Path) -> str:
    env_p = ws_root / ".env"
    if env_p.exists():
        for ln in env_p.read_text(encoding="utf-8", errors="replace").splitlines():
            s = ln.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, v = s.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k in ("NOTION_TOKEN", "NOTION_API_KEY") and v and not os.environ.get(k):
                os.environ[k] = v
    tok = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY") or ""
    if not tok:
        raise RuntimeError(
            "NOTION_TOKEN is missing. Add NOTION_TOKEN=ntn_... to .env (see docs/ECOSYSTEM_SETUP.md)."
        )
    return tok


def extract_notion_id(raw: str) -> str:
    m = re.search(r"([0-9a-f]{32}|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", raw.replace("-", "") if len(raw) == 32 else raw, re.I)
    if not m:
        cleaned = re.sub(r"[^0-9a-fA-F]", "", raw)
        if len(cleaned) >= 32:
            h = cleaned[-32:]
            return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"
        raise ValueError(f"Could not extract a 32-char Notion ID from {raw!r}")
    h = m.group(1).replace("-", "").lower()
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def notion_req(method: str, path: str, token: str, body: dict | None = None) -> dict:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        f"{NOTION_API}{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        err_txt = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Notion API {method} {path} HTTP {exc.code}: {err_txt}") from exc


def _collect_child_databases(block_id: str, token: str, depth: int = 0) -> dict[str, str]:
    found: dict[str, str] = {}
    if depth > 4:
        return found
    cursor = None
    child_pages: list[tuple[int, str]] = []
    while True:
        qs = f"?page_size=100{f'&start_cursor={cursor}' if cursor else ''}"
        try:
            res = notion_req("GET", f"/blocks/{block_id}/children{qs}", token)
        except RuntimeError:
            return found
        for blk in res.get("results", []):
            btype = blk.get("type", "")
            if btype == "child_database":
                title = (blk.get("child_database") or {}).get("title", "").strip()
                if title and title.lower() != "untitled":
                    found[title] = blk["id"]
            elif btype == "child_page" and depth < 2:
                ptitle = ((blk.get("child_page") or {}).get("title") or "").lower()
                prio = 0 if ("database" in ptitle or "vault" in ptitle) else 1
                child_pages.append((prio, blk["id"]))
            elif blk.get("has_children") and btype not in ("child_page", "child_database"):
                found.update(_collect_child_databases(blk["id"], token, depth + 1))
        if not res.get("has_more"):
            break
        cursor = res.get("next_cursor")
    for _, cp_id in sorted(child_pages, key=lambda x: x[0]):
        found.update(_collect_child_databases(cp_id, token, depth + 1))
        if len([k for k in found if _classify_db_key(k)]) >= 5:
            break
    return found


def _rt(text: str) -> list[dict]:
    txt = str(text or "")
    chunks = [txt[i : i + 1900] for i in range(0, len(txt), 1900)] or [""]
    return [{"type": "text", "text": {"content": c}} for c in chunks]


def _classify_db_key(title: str) -> str | None:
    tl = title.lower()
    if "research list" in tl or "active research" in tl:
        return "research_list_db"
    if "matrix literature" in tl or "literature matrix" in tl:
        return "matrix_literature_db"
    if "non-research" in tl or "reading queue" in tl:
        return "non_research_db"
    if "ai disclosure" in tl or "ai log" in tl:
        return "ai_log_db"
    if "topic" in tl:
        return "topic_db"
    return None


def cmd_discover(cfg_path: pathlib.Path, page_ref: str, token: str) -> None:
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    page_id = extract_notion_id(page_ref)
    dbs = _collect_child_databases(page_id, token)

    # If user pasted the frontend Command Hub sub-page, check its sibling pages under the parent root first
    if len([k for k in dbs if _classify_db_key(k)]) < 5:
        try:
            page_meta = notion_req("GET", f"/pages/{page_id}", token)
            parent = page_meta.get("parent") or {}
            if parent.get("type") == "page_id" and parent.get("page_id"):
                sibling_dbs = _collect_child_databases(parent["page_id"], token)
                for k, v in sibling_dbs.items():
                    dbs.setdefault(k, v)
        except RuntimeError:
            pass

    # Fallback: search accessible databases in case linked views point to sibling DBs
    if len([k for k in dbs if _classify_db_key(k)]) < 5:
        sr = notion_req("POST", "/search", token, {"filter": {"property": "object", "value": "database"}, "page_size": 50})
        for obj in sr.get("results", []):
            t = "".join(p.get("plain_text", "") for p in obj.get("title", [])).strip()
            if t and t not in dbs:
                dbs[t] = obj["id"]

    mapped: dict[str, str] = {}
    for title, db_id in dbs.items():
        k = _classify_db_key(title)
        if k and k not in mapped:
            mapped[k] = db_id

    integ = cfg.setdefault("integrations", {})
    notion_cfg = integ.setdefault("notion", {})
    notion_cfg["enabled"] = True
    notion_cfg["dashboard_page_id"] = page_id
    notion_cfg.update(mapped)
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: Discovered {len(mapped)} Notion template databases -> {cfg_path.name}")
    for k, v in mapped.items():
        print(f"    {k:22s}: {v}")


def _query_by_title_or_doi(db_id: str, token: str, title: str = "", doi: str = "") -> str | None:
    if doi:
        res = notion_req("POST", f"/databases/{db_id}/query", token, {"filter": {"property": "DOI", "rich_text": {"equals": doi}}, "page_size": 1})
        if res.get("results"):
            return res["results"][0]["id"]
    if title:
        res = notion_req("POST", f"/databases/{db_id}/query", token, {"filter": {"property": "Title", "title": {"equals": title}}, "page_size": 1})
        if res.get("results"):
            return res["results"][0]["id"]
    return None


def cmd_push_research(cfg_path: pathlib.Path, stage: str, target_output: str, token: str) -> None:
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    ncfg = cfg.get("integrations", {}).get("notion", {})
    db_id = ncfg.get("research_list_db")
    if not db_id:
        raise RuntimeError("Missing integrations.notion.research_list_db. Run `sync_notion.py discover` first.")

    title = cfg.get("skripsi", {}).get("judul", "Untitled Research")
    props = {
        "Title": {"title": _rt(title)},
        "Stage": {"select": {"name": stage}},
        "Target Output": {"select": {"name": target_output}},
    }
    existing_id = ncfg.get("active_research_page_id") or _query_by_title_or_doi(db_id, token, title=title)
    if existing_id:
        notion_req("PATCH", f"/pages/{existing_id}", token, {"properties": props})
        page_id = existing_id
        action = "Updated"
    else:
        created = notion_req("POST", "/pages", token, {"parent": {"database_id": db_id}, "properties": props})
        page_id = created["id"]
        action = "Created"

    ncfg["active_research_page_id"] = page_id
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: {action} Active Research in Notion -> {page_id} (Stage: {stage})")


def _ensure_topics(topic_db: str, names: list[str], token: str) -> list[str]:
    ids: list[str] = []
    for name in names:
        nm = name.strip()
        if not nm:
            continue
        res = notion_req("POST", f"/databases/{topic_db}/query", token, {"filter": {"property": "Topic", "title": {"equals": nm}}, "page_size": 1})
        if res.get("results"):
            ids.append(res["results"][0]["id"])
        else:
            cr = notion_req("POST", "/pages", token, {"parent": {"database_id": topic_db}, "properties": {"Topic": {"title": _rt(nm)}}})
            ids.append(cr["id"])
    return ids


def _build_notes_callout(item: dict) -> list[dict]:
    core = item.get("core_thesis") or item.get("Conclusion") or item.get("Key Findings") or ""
    quotes = item.get("key_quotes") or item.get("Place (Period)") or ""
    links = item.get("draft_links") or ""
    bullets = []
    for lbl, val in [("Core Thesis:", core), ("Key Quotes/Page Ref:", quotes), ("How It Links to My Draft:", links)]:
        if val:
            bullets.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [
                        {"type": "text", "text": {"content": lbl + " "}, "annotations": {"bold": True, "color": "purple"}},
                        {"type": "text", "text": {"content": str(val)[:1900]}},
                    ]
                },
            })
    if not bullets:
        return []
    return [{
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": "Reading & Appraisal Notes"}, "annotations": {"bold": True, "color": "purple"}}],
            "icon": {"type": "emoji", "emoji": "📌"},
            "color": "gray_background",
            "children": bullets,
        },
    }]


def cmd_push_literature(cfg_path: pathlib.Path, json_file: pathlib.Path, token: str) -> None:
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    ncfg = cfg.get("integrations", {}).get("notion", {})
    db_id = ncfg.get("matrix_literature_db")
    if not db_id:
        raise RuntimeError("Missing integrations.notion.matrix_literature_db. Run `sync_notion.py discover` first.")
    res_page = ncfg.get("active_research_page_id")
    topic_db = ncfg.get("topic_db")

    payload = json.loads(json_file.read_text(encoding="utf-8"))
    rows = payload if isinstance(payload, list) else payload.get("items", [])

    rich_fields = (
        "Writer", "Journal / Publisher", "DOI", "CiteKey", "Background", "Object Scope",
        "Place (Period)", "Sample", "Method", "Variable", "Key Findings", "Conclusion",
        "Discussions", "Limitations", "Gaps", "Research Contribution",
    )
    select_fields = ("Grade", "Tier", "Read Status", "Stance")

    synced = 0
    for it in rows:
        title = it.get("Title") or it.get("title") or ""
        if not title:
            continue
        doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", str(it.get("DOI") or it.get("doi") or ""), flags=re.I).strip()
        props: dict = {"Title": {"title": _rt(title)}}
        for rf in rich_fields:
            if it.get(rf):
                props[rf] = {"rich_text": _rt(it[rf])}
        if doi:
            props["DOI"] = {"rich_text": _rt(doi)}
        if it.get("Year"):
            props["Year"] = {"number": int(it["Year"])}
        if it.get("Cloud/Zotero Link"):
            props["Cloud/Zotero Link"] = {"url": str(it["Cloud/Zotero Link"])}
        for sf in select_fields:
            if it.get(sf):
                props[sf] = {"select": {"name": str(it[sf])}}
        if it.get("Evidence Role"):
            er = it["Evidence Role"] if isinstance(it["Evidence Role"], list) else [str(it["Evidence Role"])]
            props["Evidence Role"] = {"multi_select": [{"name": x} for x in er if x]}
        if it.get("Section"):
            sec = it["Section"] if isinstance(it["Section"], list) else [str(it["Section"])]
            props["Section"] = {"multi_select": [{"name": x} for x in sec if x]}
        if res_page:
            props["Related Research"] = {"relation": [{"id": res_page}]}
        if topic_db and it.get("Topics"):
            t_names = it["Topics"] if isinstance(it["Topics"], list) else [str(it["Topics"])]
            t_ids = _ensure_topics(topic_db, t_names, token)
            if t_ids:
                props["Topic"] = {"relation": [{"id": tid} for tid in t_ids]}

        existing_id = _query_by_title_or_doi(db_id, token, title=title, doi=doi)
        if existing_id:
            notion_req("PATCH", f"/pages/{existing_id}", token, {"properties": props})
        else:
            children = _build_notes_callout(it)
            body = {"parent": {"database_id": db_id}, "properties": props}
            if children:
                body["children"] = children
            notion_req("POST", "/pages", token, body)
        synced += 1
    print(f"OK: Synced {synced} literature item(s) to Notion [DB] — Matrix Literature.")


def cmd_mark_cited(cfg_path: pathlib.Path, token: str) -> None:
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    ws_root = cfg_path.parent
    ncfg = cfg.get("integrations", {}).get("notion", {})
    db_id = ncfg.get("matrix_literature_db")
    if not db_id:
        raise RuntimeError("Missing integrations.notion.matrix_literature_db.")

    zmap = json.loads((ws_root / cfg["zotero"]["map_file"]).read_text(encoding="utf-8"))
    specs = json.loads((ws_root / cfg["zotero"]["citation_specs_file"]).read_text(encoding="utf-8"))
    cited_keys = {tup[0] for sp in specs for tup in sp[1]}

    updated = 0
    for k in cited_keys:
        it = zmap.get("items", {}).get(k, {})
        doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", str(it.get("DOI") or ""), flags=re.I).strip()
        title = it.get("title", "")
        pid = _query_by_title_or_doi(db_id, token, title=title, doi=doi)
        if pid:
            notion_req("PATCH", f"/pages/{pid}", token, {"properties": {"Read Status": {"select": {"name": "Cited in Draft"}}}})
            updated += 1
    print(f"OK: Marked {updated} cited paper(s) as 'Cited in Draft' in Notion.")


def cmd_push_non_research(cfg_path: pathlib.Path, json_file: pathlib.Path, token: str) -> None:
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    ncfg = cfg.get("integrations", {}).get("notion", {})
    db_id = ncfg.get("non_research_db")
    if not db_id:
        raise RuntimeError("Missing integrations.notion.non_research_db. Run `sync_notion.py discover` first.")
    res_page = ncfg.get("active_research_page_id")
    topic_db = ncfg.get("topic_db")

    payload = json.loads(json_file.read_text(encoding="utf-8"))
    rows = payload if isinstance(payload, list) else payload.get("items", [])
    synced = 0
    for it in rows:
        title = it.get("Title") or it.get("title") or ""
        if not title:
            continue
        props: dict = {"Title": {"title": _rt(title)}}
        if it.get("Type"):
            props["Type"] = {"select": {"name": str(it["Type"])}}
        if it.get("Status"):
            props["Status"] = {"status": {"name": str(it["Status"])}}
        if it.get("Source"):
            props["Source"] = {"rich_text": _rt(it["Source"])}
        if it.get("Key Parameters"):
            props["Key Parameters"] = {"rich_text": _rt(it["Key Parameters"])}
        if it.get("Year"):
            props["Year"] = {"number": int(it["Year"])}
        if it.get("Cloud / Doc Link"):
            props["Cloud / Doc Link"] = {"url": str(it["Cloud / Doc Link"])}
        if res_page:
            props["Related Research"] = {"relation": [{"id": res_page}]}
        if topic_db and it.get("Topics"):
            t_names = it["Topics"] if isinstance(it["Topics"], list) else [str(it["Topics"])]
            t_ids = _ensure_topics(topic_db, t_names, token)
            if t_ids:
                props["Topic"] = {"relation": [{"id": tid} for tid in t_ids]}
        existing_id = _query_by_title_or_doi(db_id, token, title=title)
        if existing_id:
            notion_req("PATCH", f"/pages/{existing_id}", token, {"properties": props})
        else:
            notion_req("POST", "/pages", token, {"parent": {"database_id": db_id}, "properties": props})
        synced += 1
    print(f"OK: Synced {synced} document(s) to Notion [DB] — Non-Research Documents.")


def cmd_push_ai_log(cfg_path: pathlib.Path, json_file: pathlib.Path, token: str) -> None:
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    ncfg = cfg.get("integrations", {}).get("notion", {})
    db_id = ncfg.get("ai_log_db")
    if not db_id:
        raise RuntimeError("Missing integrations.notion.ai_log_db. Run `sync_notion.py discover` first.")
    res_page = ncfg.get("active_research_page_id")
    payload = json.loads(json_file.read_text(encoding="utf-8"))
    rows = payload if isinstance(payload, list) else payload.get("items", [])
    synced = 0
    for it in rows:
        title = it.get("GenAI Version") or it.get("title") or "AI Assistant Log"
        props: dict = {"GenAI Version": {"title": _rt(title)}}
        for rf in ("Part Using GenAI", "Objectives", "Prompt Used", "Output", "Verification"):
            if it.get(rf):
                props[rf] = {"rich_text": _rt(it[rf])}
        for nf in ("Accuracy", "Relevance", "Completeness", "Trustworthiness", "Citation Integrity"):
            if it.get(nf) is not None:
                props[nf] = {"number": int(it[nf])}
        if res_page:
            props["Related Research"] = {"relation": [{"id": res_page}]}
        notion_req("POST", "/pages", token, {"parent": {"database_id": db_id}, "properties": props})
        synced += 1
    print(f"OK: Logged {synced} AI Disclosure entry(ies) to Notion [DB] — AI Disclosure Log.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync thesis literature & stages to the Purple Notion Research Dashboard.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_disc = sub.add_parser("discover", help="Discover 5 template database IDs from duplicated Notion page")
    p_disc.add_argument("--config", type=pathlib.Path, required=True)
    p_disc.add_argument("--page", required=True, help="Duplicated Notion Dashboard URL or 32-char ID")

    p_res = sub.add_parser("push-research", help="Create or update Active Research row & Stage")
    p_res.add_argument("--config", type=pathlib.Path, required=True)
    p_res.add_argument("--stage", default="1. Ideation")
    p_res.add_argument("--target-output", default="Thesis / Dissertation")

    p_lit = sub.add_parser("push-literature", help="Upsert dissected papers to [DB] — Matrix Literature")
    p_lit.add_argument("--config", type=pathlib.Path, required=True)
    p_lit.add_argument("--json-file", type=pathlib.Path, required=True)

    p_cit = sub.add_parser("mark-cited", help="Update Read Status='Cited in Draft' for all cited items")
    p_cit.add_argument("--config", type=pathlib.Path, required=True)

    p_nr = sub.add_parser("push-non-research", help="Upsert statutes/reports/data to [DB] — Non-Research Documents")
    p_nr.add_argument("--config", type=pathlib.Path, required=True)
    p_nr.add_argument("--json-file", type=pathlib.Path, required=True)

    p_ai = sub.add_parser("push-ai-log", help="Log TRACC audit entry to [DB] — AI Disclosure Log")
    p_ai.add_argument("--config", type=pathlib.Path, required=True)
    p_ai.add_argument("--json-file", type=pathlib.Path, required=True)

    args = parser.parse_args()
    ws_root = args.config.resolve().parent
    token = load_token(ws_root)

    if args.cmd == "discover":
        cmd_discover(args.config.resolve(), args.page, token)
    elif args.cmd == "push-research":
        cmd_push_research(args.config.resolve(), args.stage, args.target_output, token)
    elif args.cmd == "push-literature":
        cmd_push_literature(args.config.resolve(), args.json_file.resolve(), token)
    elif args.cmd == "mark-cited":
        cmd_mark_cited(args.config.resolve(), token)
    elif args.cmd == "push-non-research":
        cmd_push_non_research(args.config.resolve(), args.json_file.resolve(), token)
    elif args.cmd == "push-ai-log":
        cmd_push_ai_log(args.config.resolve(), args.json_file.resolve(), token)


if __name__ == "__main__":
    main()
