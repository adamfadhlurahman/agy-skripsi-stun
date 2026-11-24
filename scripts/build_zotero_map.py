"""Build zotero_map.json from Zotero Desktop Local API or an exported CSL JSON file."""

from __future__ import annotations

import argparse
import json
import pathlib
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


def load_from_csl_json(csl_path: pathlib.Path, user_id: str, collection_key: str) -> dict:
    raw = json.loads(csl_path.read_text(encoding="utf-8"))
    raw_items = raw.get("items", raw) if isinstance(raw, dict) else raw
    items_map: dict[str, dict] = {}
    prefix = f"http://zotero.org/users/{user_id}/items/"
    for item in raw_items:
        uri = str(item.get("id", ""))
        key = uri.rstrip("/").split("/")[-1] if "/" in uri else uri
        if not key:
            continue
        items_map[key] = item
    return {
        "collection_key": collection_key,
        "user_uri_prefix": prefix,
        "csl_schema": CSL_SCHEMA,
        "items": items_map,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build zotero_map.json for build_thesis_docx.py.")
    parser.add_argument("--list-collections", action="store_true", help="List available Zotero collections and keys")
    parser.add_argument("--collection", default="", help="Zotero collection key (optional)")
    parser.add_argument("--collection-name", default="", help="Zotero collection name (auto-resolves key)")
    parser.add_argument("--user-id", default="0", help="Zotero local API user id (default: 0)")
    parser.add_argument("--csl-json", type=pathlib.Path, default=None, help="Fallback path to exported Zotero CSL JSON file")
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

    if args.csl_json is not None:
        zmap = load_from_csl_json(args.csl_json, args.user_id, col_key)
    else:
        zmap = fetch_from_local_api(args.user_id, col_key)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(zmap, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: Wrote {len(zmap['items'])} Zotero items -> {args.out}")


if __name__ == "__main__":
    main()
