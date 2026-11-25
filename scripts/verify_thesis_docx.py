"""Structural, live Zotero field, and STUN formatting verifier for built Proposal/Thesis DOCX."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import zipfile
from lxml import etree

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def w(t: str) -> str:
    return f"{{{W_NS}}}{t}"


def verify_docx(docx_path: pathlib.Path, mode: str, require_keaslian: bool = True, provider: str = "zotero") -> None:
    assert docx_path.exists(), f"Target DOCX missing: {docx_path}"
    with zipfile.ZipFile(docx_path, "r") as z:
        if provider == "zotero":
            assert "docProps/custom.xml" in z.namelist(), "Missing docProps/custom.xml (ZOTERO_PREF_1)"
            custom_txt = z.read("docProps/custom.xml").decode("utf-8", errors="replace")
            assert "ZOTERO_PREF_1" in custom_txt, "Missing ZOTERO_PREF_1 in custom.xml"

        doc = etree.fromstring(z.read("word/document.xml"))
        body = doc.find(w("body"))

        subbabs, bsubbabs, l4s, l5s = [], [], [], []
        zot_items, zot_bibl = 0, 0
        toc_fields, seq_fields = 0, 0

        for p in body.findall(f".//{w('p')}"):
            ps = p.find(f"./{w('pPr')}/{w('pStyle')}")
            st = ps.get(w("val")) if ps is not None else ""
            txt = "".join(t.text or "" for t in p.findall(f".//{w('t')}")).strip()

            buf = None
            for el in p.iter():
                if el.tag == w("fldChar"):
                    ft = el.get(w("fldCharType"))
                    if ft == "begin":
                        buf = []
                    elif ft in ("separate", "end") and buf is not None:
                        ins = "".join(buf).strip()
                        buf = None
                        if "ADDIN ZOTERO_ITEM" in ins:
                            zot_items += 1
                        elif "ADDIN ZOTERO_BIBL" in ins:
                            zot_bibl += 1
                        elif ins.startswith("TOC ") or " TOC " in f" {ins} ":
                            toc_fields += 1
                        elif ins.startswith("SEQ ") or " SEQ " in f" {ins} ":
                            seq_fields += 1
                elif el.tag == w("instrText") and buf is not None and el.text:
                    buf.append(el.text)

            if st == "JudulSubbab":
                assert not re.match(r"^\d+\.\d+\s+", txt), f"Hardcoded prefix in JudulSubbab: {txt!r}"
                subbabs.append(txt)
            elif st == "JudulBagianSubbab":
                assert not re.match(r"^\d+\.\d+\.\d+\s+", txt), f"Hardcoded prefix in JudulBagianSubbab: {txt!r}"
                bsubbabs.append(txt)
            elif st == "JudulBagianBagian-Subbab":
                assert not re.match(r"^\d+\.\d+\.\d+\.\d+\s+", txt), f"Hardcoded prefix in level-4 heading: {txt!r}"
                l4s.append(txt)
            elif st == "JusulSubbagianbagian-subbab":
                assert not re.match(r"^\d+\.\d+\.\d+\.\d+\.\d+\s+", txt), f"Hardcoded prefix in level-5 heading: {txt!r}"
                l5s.append(txt)

        full_text = "".join(t.text or "" for t in body.findall(f".//{w('t')}"))
        for bad_tok in ("Error! Bookmark not defined", "Error! Reference source not found"):
            assert bad_tok not in full_text, f"Unresolved Word error field: {bad_tok}"

        bad_pronouns = re.findall(r"\b(?:saya|aku|kami|kita|anda)\b", full_text.lower())
        assert not bad_pronouns, f"Forbidden first/second-person pronouns found: {bad_pronouns[:10]}"

        if mode == "thesis" and require_keaslian:
            assert "PERNYATAAN KEASLIAN" in full_text.upper(), "Missing Originality Statement in Thesis DOCX"

        sects = doc.findall(f".//{w('sectPr')}")
        min_sects = 5 if mode == "proposal" else 7
        assert len(sects) >= min_sects, f"Expected >= {min_sects} sections for {mode}, got {len(sects)}"

        blips = [el for el in doc.iter() if el.tag.endswith("}blip")]
        print(f"[PASS] {docx_path.name} ({mode}, provider={provider}):")
        print(f"       - Sections: {len(sects)} | Images: {len(blips)} | H2: {len(subbabs)} | H3: {len(bsubbabs)} | H4: {len(l4s)} | H5: {len(l5s)}")
        print(f"       - Live fields: {toc_fields} TOC | {seq_fields} SEQ | {zot_items} ZOTERO_ITEM | {zot_bibl} ZOTERO_BIBL")
        print("       - Forbidden first/second-person pronouns: 0")


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify built Proposal or Complete Thesis DOCX.")
    parser.add_argument("--config", type=pathlib.Path, required=True, help="Path to thesis_config.json")
    parser.add_argument("--mode", choices=["proposal", "thesis", "skripsi"], default="thesis")
    args = parser.parse_args()
    mode = "thesis" if args.mode in ("thesis", "skripsi") else "proposal"

    cfg_path = args.config.resolve()
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    zmap_rel = cfg.get("zotero", {}).get("map_file", "")
    zmap_p = (cfg_path.parent / zmap_rel) if zmap_rel else None
    zmap = json.loads(zmap_p.read_text(encoding="utf-8")) if (zmap_p and zmap_p.exists()) else {}
    provider = (cfg.get("citation_provider") or cfg.get("zotero", {}).get("provider") or zmap.get("provider") or "zotero").strip().lower()
    out_key = "output_proposal_docx" if mode == "proposal" else "output_skripsi_docx"
    req_keaslian = cfg.get("skripsi", {}).get("include_keaslian_page", True)
    verify_docx(cfg_path.parent / cfg["paths"][out_key], mode, require_keaslian=req_keaslian, provider=provider)


if __name__ == "__main__":
    main()
