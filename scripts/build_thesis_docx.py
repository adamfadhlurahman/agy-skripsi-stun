"""
Config-driven Proposal / Complete Thesis DOCX builder conforming to PER-9/PKN/2020
with native Word styles (BAB -> 1.1.1.1.1, Kutipan Langsung), live TOC/SEQ/PAGE fields,
live Zotero CSL fields, complete Front Matter, Appendices, and Curriculum Vitae.
"""

from __future__ import annotations

import argparse
import copy
import html
import json
import pathlib
import re
import secrets
import string
import urllib.request
import zipfile
from html.parser import HTMLParser
from lxml import etree

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt, RGBColor

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
RELS_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CP_NS = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC_NS = "http://purl.org/dc/elements/1.1/"

XSD_STYLE_ORDER = [
    "name", "aliases", "basedOn", "next", "link", "autoRedefine", "hidden",
    "uiPriority", "semiHidden", "unhideWhenUsed", "qFormat", "locked", "personal",
    "personalCompose", "personalReply", "rsid", "pPr", "rPr", "tblPr", "trPr",
    "tcPr", "tblStylePr",
]
XSD_PPR_ORDER = [
    "pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl",
    "numPr", "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens",
    "kinsoku", "wordWrap", "overflowPunct", "topLinePunct", "autoSpaceDE",
    "autoSpaceDN", "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind",
    "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc", "textDirection",
    "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle",
    "rPr", "sectPr", "pPrChange",
]
XSD_RPR_ORDER = [
    "rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike",
    "dstrike", "outline", "shadow", "emboss", "imprint", "noProof", "snapToGrid",
    "vanish", "webHidden", "color", "spacing", "w", "kern", "position", "sz",
    "szCs", "highlight", "u", "effect", "bdr", "shd", "fitText", "vertAlign",
    "rtl", "cs", "em", "lang", "eastAsianLayout", "specVanish", "oMath",
]
XSD_TBLPR_ORDER = [
    "tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize",
    "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd", "tblBorders",
    "shd", "tblLayout", "tblCellMar", "tblLook", "tblCaption", "tblDescription",
]
XSD_LVL_ORDER = [
    "start", "numFmt", "lvlRestart", "pStyle", "isLgl", "suff", "lvlText",
    "lvlPicBulletId", "legacy", "lvlJc", "pPr", "rPr",
]


def w(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


def gen_cit_id() -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(8))


def insert_xsd_order(parent, child, order_list):
    tag = child.tag.split("}")[-1]
    rank = {name: i for i, name in enumerate(order_list)}
    target_rank = rank.get(tag, len(order_list))
    for idx, el in enumerate(list(parent)):
        if rank.get(el.tag.split("}")[-1], len(order_list)) > target_rank:
            parent.insert(idx, child)
            return child
    parent.append(child)
    return child


def get_or_add_xsd(parent, ns_tag, order_list):
    el = parent.find(ns_tag)
    if el is None:
        el = etree.Element(ns_tag)
        insert_xsd_order(parent, el, order_list)
    return el


def set_run_font(run, size_pt=12, bold=False, italic=False, subscript=False, superscript=False):
    run.font.name = "Times New Roman"
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    run.font.subscript = subscript
    run.font.superscript = superscript
    run.font.color.rgb = RGBColor(0, 0, 0)
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    for attr in ("ascii", "eastAsia", "hAnsi", "cs"):
        rFonts.set(qn(f"w:{attr}"), "Times New Roman")


def set_borderless_table(table):
    tblPr = table._tbl.tblPr
    tb = tblPr.find(qn("w:tblBorders"))
    if tb is not None:
        tblPr.remove(tb)
    tblBorders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        '<w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/>'
        '<w:right w:val="none"/><w:insideH w:val="none"/><w:insideV w:val="none"/>'
        '</w:tblBorders>'
    )
    insert_xsd_order(tblPr, tblBorders, XSD_TBLPR_ORDER)


def add_fld_char(paragraph, fld_type, size_pt=12, bold=False):
    r = paragraph.add_run()
    set_run_font(r, size_pt=size_pt, bold=bold)
    r._r.append(parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="{fld_type}"/>'))
    return r


def add_instr_text(paragraph, instr_str, size_pt=12, bold=False):
    r = paragraph.add_run()
    set_run_font(r, size_pt=size_pt, bold=bold)
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instr_str
    r._r.append(instr)
    return r


def add_field(paragraph, instr_str, placeholder_text="", size_pt=12, bold=False):
    add_fld_char(paragraph, "begin", size_pt=size_pt, bold=bold)
    add_instr_text(paragraph, instr_str, size_pt=size_pt, bold=bold)
    add_fld_char(paragraph, "separate", size_pt=size_pt, bold=bold)
    if placeholder_text:
        set_run_font(paragraph.add_run(placeholder_text), size_pt=size_pt, bold=bold)
    add_fld_char(paragraph, "end", size_pt=size_pt, bold=bold)


def append_non_citation_markdown(paragraph, text, size_pt=12, base_bold=False, base_italic=False):
    toks = re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)", text)
    for tok in toks:
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**"):
            set_run_font(paragraph.add_run(tok[2:-2]), size_pt=size_pt, bold=True, italic=base_italic)
        elif tok.startswith("*") and tok.endswith("*"):
            set_run_font(paragraph.add_run(tok[1:-1]), size_pt=size_pt, bold=base_bold, italic=True)
        elif tok.startswith("`") and tok.endswith("`"):
            set_run_font(paragraph.add_run(tok[1:-1]), size_pt=size_pt, bold=base_bold, italic=base_italic)
        else:
            set_run_font(paragraph.add_run(tok), size_pt=size_pt, bold=base_bold, italic=base_italic)


def append_with_italic_phrases(paragraph, text: str, phrases: list[str], size_pt=12, bold=False):
    clean_phrases = [p for p in (phrases or []) if p]
    if not clean_phrases:
        set_run_font(paragraph.add_run(text), size_pt=size_pt, bold=bold)
        return
    pat = "(" + "|".join(re.escape(p) for p in sorted(clean_phrases, key=len, reverse=True)) + ")"
    for part in re.split(pat, text, flags=re.I):
        if not part:
            continue
        is_it = any(part.lower() == p.lower() for p in clean_phrases)
        set_run_font(paragraph.add_run(part), size_pt=size_pt, bold=bold, italic=is_it)


class CitationEngine:
    def __init__(self, zmap: dict, specs_list: list):
        self.zmap = zmap or {}
        self.specs = {sp[0]: sp for sp in (specs_list or [])}
        self.emitted_keys: list[str] = []
        if self.specs:
            pat = "|".join(re.escape(k) for k in sorted(self.specs, key=lambda x: -len(x)))
            self.regex = re.compile(pat)
        else:
            self.regex = None

    def build_csl_payload(self, display_text: str, item_tuples: list) -> dict:
        citation_items = []
        prefix = self.zmap.get("user_uri_prefix", "http://zotero.org/users/0/items/")
        items = self.zmap.get("items", {})
        for idx, tup in enumerate(item_tuples, 1):
            key, locator, label, suppress_author = tup
            entry = {
                "id": idx,
                "uris": [f"{prefix}{key}"],
                "itemData": items.get(key, {"id": key, "title": key}),
            }
            if locator:
                entry["locator"] = locator
                entry["label"] = label or "page"
            if suppress_author:
                entry["suppress-author"] = True
            citation_items.append(entry)
            if key not in self.emitted_keys:
                self.emitted_keys.append(key)
        return {
            "citationID": gen_cit_id(),
            "properties": {
                "formattedCitation": display_text,
                "plainCitation": display_text,
                "noteIndex": 0,
            },
            "citationItems": citation_items,
            "schema": self.zmap.get("csl_schema", "https://github.com/citation-style-language/schema/raw/master/csl-citation.json"),
        }

    def append_rich_line(self, paragraph, text: str, size_pt=12, base_bold=False, base_italic=False):
        if self.regex is None:
            append_non_citation_markdown(paragraph, text, size_pt=size_pt, base_bold=base_bold, base_italic=base_italic)
            return
        pos = 0
        for m in self.regex.finditer(text):
            if m.start() > pos:
                append_non_citation_markdown(paragraph, text[pos:m.start()], size_pt=size_pt, base_bold=base_bold, base_italic=base_italic)
            matched = m.group(0)
            spec = self.specs[matched]
            if len(spec) == 2:
                _, item_tuples = spec
                prefix, field_display = "", matched
            else:
                _, item_tuples, prefix, field_display = spec
            if prefix:
                set_run_font(paragraph.add_run(prefix), size_pt=size_pt, bold=base_bold, italic=base_italic)
            payload = self.build_csl_payload(field_display, item_tuples)
            add_fld_char(paragraph, "begin", size_pt=size_pt)
            add_instr_text(paragraph, f" ADDIN ZOTERO_ITEM CSL_CITATION {json.dumps(payload, ensure_ascii=False)} ", size_pt=size_pt)
            add_fld_char(paragraph, "separate", size_pt=size_pt)
            set_run_font(paragraph.add_run(field_display), size_pt=size_pt, bold=base_bold, italic=base_italic)
            add_fld_char(paragraph, "end", size_pt=size_pt)
            pos = m.end()
        if pos < len(text):
            append_non_citation_markdown(paragraph, text[pos:], size_pt=size_pt, base_bold=base_bold, base_italic=base_italic)


def prepare_base_template(cfg: dict, mode: str, tmp_docx: pathlib.Path, ws_root: pathlib.Path) -> None:
    src = ws_root / cfg["paths"]["template_docx"]
    parser = etree.XMLParser(remove_blank_text=False)
    mhs = cfg["mahasiswa"]
    pmb = cfg["pembimbing"]
    skr = cfg["skripsi"]
    zot = cfg["zotero"]

    doc_type_lbl = "PROPOSAL SKRIPSI" if mode == "proposal" else "SKRIPSI"
    persetujuan_2 = "PROPOSAL SKRIPSI" if mode == "proposal" else "SKRIPSI"
    jenjang = mhs.get("jenjang_gelar", "Sarjana Terapan")
    italic_phrases = skr.get("italic_phrases_in_title", [])

    def replace_p(p_el, lines_list, apply_italic=False):
        ppr = p_el.find(w("pPr"))
        first_r = p_el.find(w("r"))
        rpr = copy.deepcopy(first_r.find(w("rPr"))) if (first_r is not None and first_r.find(w("rPr")) is not None) else None
        for ch in list(p_el):
            if ch is not ppr:
                p_el.remove(ch)

        def emit_run(txt_val, is_it=False):
            nr = etree.SubElement(p_el, w("r"))
            nr_rpr = copy.deepcopy(rpr) if rpr is not None else etree.Element(w("rPr"))
            if is_it:
                for tag_i in ("i", "iCs"):
                    if nr_rpr.find(w(tag_i)) is None:
                        insert_xsd_order(nr_rpr, etree.Element(w(tag_i)), XSD_RPR_ORDER)
                    else:
                        el_i = nr_rpr.find(w(tag_i))
                        if w("val") in el_i.attrib:
                            del el_i.attrib[w("val")]
            nr.append(nr_rpr)
            t = etree.SubElement(nr, w("t"))
            t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            t.text = txt_val

        for idx, txt in enumerate(lines_list):
            if idx > 0:
                br_r = etree.SubElement(p_el, w("r"))
                if rpr is not None:
                    br_r.append(copy.deepcopy(rpr))
                etree.SubElement(br_r, w("br"))
            if apply_italic and italic_phrases:
                pat = "(" + "|".join(re.escape(ph) for ph in sorted(italic_phrases, key=len, reverse=True) if ph) + ")"
                for part in re.split(pat, txt, flags=re.I):
                    if not part:
                        continue
                    is_it = any(part.lower() == ph.lower() for ph in italic_phrases)
                    emit_run(part, is_it=is_it)
            else:
                emit_run(txt, is_it=False)

    with zipfile.ZipFile(src, "r") as zin:
        doc_root = etree.fromstring(zin.read("word/document.xml"), parser)
        body = doc_root.find(w("body"))
        children = list(body)

        # Cover header & fields inside template
        hdr_lines = mhs.get("header_lines") or [
            "KEMENTERIAN KEUANGAN REPUBLIK INDONESIA",
            "BADAN PENDIDIKAN DAN PELATIHAN KEUANGAN",
            mhs.get("kampus", "POLITEKNIK KEUANGAN NEGARA STAN").upper(),
            mhs.get("kota_kampus", "Tangerang Selatan").upper(),
        ]
        replace_p(children[0], hdr_lines)
        replace_p(children[4], [doc_type_lbl])
        replace_p(children[6], [skr["judul"].upper()], apply_italic=True)
        replace_p(children[8], ["Diajukan oleh:", mhs["nama"], f"NPM {mhs['npm']}"])
        replace_p(children[13], [f"Guna Mencapai Gelar {jenjang} {mhs['prodi'].title()}"])
        replace_p(children[14], [str(mhs["tahun_lulus"])])

        # Halaman Persetujuan
        replace_p(children[18], hdr_lines)
        replace_p(children[20], ["PERSETUJUAN"])
        replace_p(children[21], [persetujuan_2])
        tbl_info = children[23]
        for r_idx, val in enumerate([
            mhs["nama"].upper(),
            mhs["npm"],
            mhs["prodi"].upper(),
            mhs["bidang_studi"].upper(),
            skr["judul"].upper(),
        ]):
            tcs = tbl_info.findall(f"./{w('tr')}[{r_idx + 1}]/{w('tc')}")
            if len(tcs) >= 3:
                ps = tcs[2].findall(f"./{w('p')}")
                if ps:
                    replace_p(ps[0], [val], apply_italic=(r_idx == 4))

        tbl_sig = children[26]
        sig_tcs = tbl_sig.findall(f"./{w('tr')}[1]/{w('tc')}")
        if len(sig_tcs) >= 2:
            ps0 = sig_tcs[0].findall(f"./{w('p')}")
            ps1 = sig_tcs[1].findall(f"./{w('p')}")
            if len(ps0) >= 6:
                replace_p(ps0[-2], [pmb["ketua_prodi"]])
                replace_p(ps0[-1], [f"NIP {pmb['nip_kaprodi']}"])
            if len(ps1) >= 6:
                replace_p(ps1[-2], [pmb["dosen_pembimbing"]])
                replace_p(ps1[-1], [f"NIP {pmb['nip_pembimbing']}"])

        for cov_idx in (1, 19):
            c_ppr = children[cov_idx].find(w("pPr"))
            if c_ppr is not None:
                c_ps = c_ppr.find(w("pStyle"))
                if c_ps is not None:
                    c_ps.set(w("val"), "JUDULAWAL")

        final_sect = copy.deepcopy(children[-1]) if children[-1].tag == w("sectPr") else None
        for ch in children[29:]:
            body.remove(ch)
        if final_sect is not None:
            body.append(final_sect)

        new_doc_xml = etree.tostring(doc_root, xml_declaration=True, encoding="UTF-8", standalone=True)

        # Ensure JUDULAWAL style & clean STUN styles across all 5 heading levels + KutipanLangsung
        styles_root = etree.fromstring(zin.read("word/styles.xml"), parser)

        def patch_style(sid, fn):
            for st in styles_root.findall(w("style")):
                if st.get(w("styleId")) == sid:
                    fn(st)

        def ensure_rpr(el):
            parent_order = XSD_STYLE_ORDER if el.tag.split("}")[-1] == "style" else XSD_LVL_ORDER
            rpr = get_or_add_xsd(el, w("rPr"), parent_order)
            rf = get_or_add_xsd(rpr, w("rFonts"), XSD_RPR_ORDER)
            for attr in ("ascii", "eastAsia", "hAnsi", "cs"):
                rf.set(w(attr), "Times New Roman")
            col = get_or_add_xsd(rpr, w("color"), XSD_RPR_ORDER)
            col.set(w("val"), "000000")
            return rpr

        def set_sz(rpr, val):
            for tag in ("sz", "szCs"):
                get_or_add_xsd(rpr, w(tag), XSD_RPR_ORDER).set(w("val"), str(val))

        def set_toggle(rpr, tag, on=True):
            el = get_or_add_xsd(rpr, w(tag), XSD_RPR_ORDER)
            if on:
                if w("val") in el.attrib:
                    del el.attrib[w("val")]
            else:
                el.set(w("val"), "0")

        for st in list(styles_root.findall(w("style"))):
            if st.get(w("styleId")) == "JUDULBAB":
                jaw = copy.deepcopy(st)
                jaw.set(w("styleId"), "JUDULAWAL")
                nm = jaw.find(w("name"))
                if nm is not None:
                    nm.set(w("val"), "JUDUL AWAL")
                ppr_jaw = get_or_add_xsd(jaw, w("pPr"), XSD_STYLE_ORDER)
                for old_np in list(ppr_jaw.findall(w("numPr"))):
                    ppr_jaw.remove(old_np)
                get_or_add_xsd(ppr_jaw, w("keepNext"), XSD_PPR_ORDER)
                sp = get_or_add_xsd(ppr_jaw, w("spacing"), XSD_PPR_ORDER)
                sp.set(w("before"), "0"); sp.set(w("after"), "360"); sp.set(w("line"), "480"); sp.set(w("lineRule"), "auto")
                get_or_add_xsd(ppr_jaw, w("jc"), XSD_PPR_ORDER).set(w("val"), "center")
                rpr_jaw = ensure_rpr(jaw)
                set_sz(rpr_jaw, 28)
                set_toggle(rpr_jaw, "b", True); set_toggle(rpr_jaw, "bCs", True)
                styles_root.append(jaw)
                break

        for sid in ("JudulSubbab", "JudulBagianSubbab"):
            def _fix_sub_bold(s):
                ppr = get_or_add_xsd(s, w("pPr"), XSD_STYLE_ORDER)
                get_or_add_xsd(ppr, w("keepNext"), XSD_PPR_ORDER)
                rpr = ensure_rpr(s)
                set_sz(rpr, 24)
                set_toggle(rpr, "b", True); set_toggle(rpr, "bCs", True)
                set_toggle(rpr, "i", False); set_toggle(rpr, "iCs", False)
            patch_style(sid, _fix_sub_bold)

        for sid in ("JudulBagianBagian-Subbab", "JusulSubbagianbagian-subbab"):
            def _fix_sub_reg(s):
                ppr = get_or_add_xsd(s, w("pPr"), XSD_STYLE_ORDER)
                get_or_add_xsd(ppr, w("keepNext"), XSD_PPR_ORDER)
                rpr = ensure_rpr(s)
                set_sz(rpr, 24)
                set_toggle(rpr, "b", False); set_toggle(rpr, "bCs", False)
                set_toggle(rpr, "i", False); set_toggle(rpr, "iCs", False)
            patch_style(sid, _fix_sub_reg)

        def _fix_kutipan(s):
            ppr = get_or_add_xsd(s, w("pPr"), XSD_STYLE_ORDER)
            sp = get_or_add_xsd(ppr, w("spacing"), XSD_PPR_ORDER)
            sp.set(w("before"), "0"); sp.set(w("after"), "120"); sp.set(w("line"), "240"); sp.set(w("lineRule"), "auto")
            ind = get_or_add_xsd(ppr, w("ind"), XSD_PPR_ORDER)
            ind.set(w("left"), "720"); ind.set(w("right"), "720"); ind.set(w("firstLine"), "0")
            get_or_add_xsd(ppr, w("jc"), XSD_PPR_ORDER).set(w("val"), "both")
            rpr = ensure_rpr(s)
            set_sz(rpr, 24)
        patch_style("KutipanLangsung", _fix_kutipan)

        new_styles_xml = etree.tostring(styles_root, xml_declaration=True, encoding="UTF-8", standalone=True)

        # Clean numbering levels 1..4 in abstractNumId=5 to latest STUN spec
        num_root = etree.fromstring(zin.read("word/numbering.xml"), parser)
        for anum in num_root.findall(w("abstractNum")):
            if anum.get(w("abstractNumId")) == "5":
                for lvl in anum.findall(w("lvl")):
                    ilvl = lvl.get(w("ilvl"))
                    if ilvl in ("1", "2"):
                        rpr = ensure_rpr(lvl)
                        set_sz(rpr, 24)
                        set_toggle(rpr, "b", True); set_toggle(rpr, "bCs", True)
                        set_toggle(rpr, "i", False); set_toggle(rpr, "iCs", False)
                    elif ilvl in ("3", "4"):
                        rpr = ensure_rpr(lvl)
                        set_sz(rpr, 24)
                        set_toggle(rpr, "b", False); set_toggle(rpr, "bCs", False)
                        set_toggle(rpr, "i", False); set_toggle(rpr, "iCs", False)
        new_num_xml = etree.tostring(num_root, xml_declaration=True, encoding="UTF-8", standalone=True)

        locale = zot.get("locale", "id-ID")
        style_url = zot.get("style", "http://www.zotero.org/styles/apa")
        custom_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n'
            '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/custom-properties" '
            'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
            '<property fmtid="{D5CDD505-2E9C-101B-9397-08002B2CF9AE}" pid="2" name="ZOTERO_PREF_1">'
            '<vt:lpwstr>&lt;data data-version="3" zotero-version="10.0.8"&gt;'
            f'&lt;session id="{gen_cit_id()}"/&gt;'
            f'&lt;style id="{style_url}" locale="{locale}" hasBibliography="1" bibliographyStyleHasBeenSet="1"/&gt;'
            '&lt;prefs&gt;&lt;pref name="fieldType" value="Field"/&gt;&lt;/prefs&gt;'
            '&lt;/data&gt;</vt:lpwstr></property></Properties>'
        ).encode("utf-8")

        core_root = etree.fromstring(zin.read("docProps/core.xml"), parser)
        for ns, tag, val in [
            (DC_NS, "title", skr["judul"]),
            (DC_NS, "creator", mhs["nama"]),
            (CP_NS, "lastModifiedBy", mhs["nama"]),
            (DC_NS, "description", ""),
        ]:
            el = core_root.find(f"{{{ns}}}{tag}")
            if el is not None:
                el.text = val
        new_core_xml = etree.tostring(core_root, xml_declaration=True, encoding="UTF-8", standalone=True)

        tmp_docx.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(tmp_docx, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "word/document.xml":
                    zout.writestr(item.filename, new_doc_xml)
                elif item.filename == "word/styles.xml":
                    zout.writestr(item.filename, new_styles_xml)
                elif item.filename == "word/numbering.xml":
                    zout.writestr(item.filename, new_num_xml)
                elif item.filename == "docProps/custom.xml":
                    zout.writestr(item.filename, custom_xml)
                elif item.filename == "docProps/core.xml":
                    zout.writestr(item.filename, new_core_xml)
                else:
                    zout.writestr(item, zin.read(item.filename))


def clear_hf(hf):
    hf.is_linked_to_previous = False
    for p in list(hf.paragraphs)[1:]:
        p._element.getparent().remove(p._element)
    p0 = hf.paragraphs[0]
    ppr = p0._p.find(qn("w:pPr"))
    for ch in list(p0._p):
        if ch is not ppr:
            p0._p.remove(ch)
    return p0


def configure_front_section(sec, start_roman=2):
    sec.page_width = Cm(21.0); sec.page_height = Cm(29.7)
    sec.left_margin = Cm(4.0); sec.right_margin = Cm(3.0)
    sec.top_margin = Cm(4.0); sec.bottom_margin = Cm(3.0)
    sec.header_distance = Cm(1.5); sec.footer_distance = Cm(1.5)
    sec.different_first_page_header_footer = False
    sectPr = sec._sectPr
    for old_pg in sectPr.findall(qn("w:pgNumType")):
        sectPr.remove(old_pg)
    pg = OxmlElement("w:pgNumType")
    pg.set(qn("w:fmt"), "lowerRoman"); pg.set(qn("w:start"), str(start_roman))
    insert_xsd_order(sectPr, pg, ("pgSz", "pgMar", "paperSrc", "pgBorders", "lnNumType", "pgNumType", "cols"))
    hp = clear_hf(sec.header)
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    add_field(hp, " PAGE ", "ii", size_pt=12)
    clear_hf(sec.footer)


def configure_chapter_section(sec, start_decimal=None, first_page_bottom=True):
    sec.page_width = Cm(21.0); sec.page_height = Cm(29.7)
    sec.left_margin = Cm(4.0); sec.right_margin = Cm(3.0)
    sec.top_margin = Cm(4.0); sec.bottom_margin = Cm(3.0)
    sec.header_distance = Cm(1.5); sec.footer_distance = Cm(1.5)
    sec.different_first_page_header_footer = first_page_bottom
    sectPr = sec._sectPr
    for old_pg in sectPr.findall(qn("w:pgNumType")):
        sectPr.remove(old_pg)
    pg = OxmlElement("w:pgNumType")
    pg.set(qn("w:fmt"), "decimal")
    if start_decimal is not None:
        pg.set(qn("w:start"), str(start_decimal))
    insert_xsd_order(sectPr, pg, ("pgSz", "pgMar", "paperSrc", "pgBorders", "lnNumType", "pgNumType", "cols"))
    hp = clear_hf(sec.header)
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    add_field(hp, " PAGE ", "1", size_pt=12)
    clear_hf(sec.footer)
    if first_page_bottom:
        clear_hf(sec.first_page_header)
        ffp = clear_hf(sec.first_page_footer)
        ffp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_field(ffp, " PAGE ", "1", size_pt=12)


def add_top_spacer(doc):
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0); sp.paragraph_format.space_after = Pt(0)
    sp.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    sp.paragraph_format.line_spacing = Cm(3.5)
    set_run_font(sp.add_run(""), size_pt=1)


def add_judul_bab(doc, line1, line2=None, style_name="JUDUL BAB"):
    p = doc.add_paragraph()
    p.style = doc.styles[style_name]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(36) if line2 else Pt(24)
    p.paragraph_format.line_spacing = 2.0 if line2 else 1.5
    p.paragraph_format.keep_with_next = True
    set_run_font(p.add_run(line1), size_pt=14, bold=True)
    if line2:
        p.add_run().add_break()
        set_run_font(p.add_run(line2), size_pt=14, bold=True)
    return p


def add_front_header_block(doc, cfg: dict):
    mhs = cfg["mahasiswa"]
    hdr_lines = mhs.get("header_lines") or [
        "KEMENTERIAN KEUANGAN REPUBLIK INDONESIA",
        "BADAN PENDIDIKAN DAN PELATIHAN KEUANGAN",
        mhs.get("kampus", "POLITEKNIK KEUANGAN NEGARA STAN").upper(),
        mhs.get("kota_kampus", "Tangerang Selatan").upper(),
    ]
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.15
    for idx, ln in enumerate(hdr_lines):
        if idx > 0:
            p.add_run().add_break()
        set_run_font(p.add_run(ln), size_pt=12, bold=True)


def add_identity_table_block(doc, cfg: dict):
    mhs = cfg["mahasiswa"]
    skr = cfg["skripsi"]
    italic_phrases = skr.get("italic_phrases_in_title", [])
    rows = [
        ("NAMA", ":", mhs["nama"].upper()),
        ("NOMOR POKOK MAHASISWA", ":", mhs["npm"]),
        ("PROGRAM STUDI", ":", mhs["prodi"].upper()),
        ("BIDANG STUDI", ":", mhs["bidang_studi"].upper()),
        ("JUDUL SKRIPSI", ":", skr["judul"].upper()),
    ]
    tbl = doc.add_table(rows=len(rows), cols=3)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    set_borderless_table(tbl)
    for r_i, (lbl, sep, val) in enumerate(rows):
        for c_i, (txt, cw) in enumerate(zip((lbl, sep, val), (Cm(5.2), Cm(0.5), Cm(8.3)))):
            cell = tbl.cell(r_i, c_i)
            cell.width = cw
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.first_line_indent = Cm(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            if r_i == 4 and c_i == 2:
                append_with_italic_phrases(p, txt, italic_phrases, size_pt=12)
            else:
                set_run_font(p.add_run(txt), size_pt=12)


def add_lulus_and_keaslian_pages(doc, cfg: dict):
    mhs = cfg["mahasiswa"]
    pmb = cfg["pembimbing"]
    skr = cfg["skripsi"]
    kota = mhs.get("kota_kampus", "Tangerang Selatan")
    tahun = str(mhs["tahun_lulus"])

    if skr.get("include_lulus_page", True):
        doc.add_page_break()
        add_front_header_block(doc, cfg)
        p_h = add_judul_bab(doc, "PERNYATAAN LULUS DARI TIM PENILAI", "SKRIPSI", style_name="JUDUL AWAL")
        p_h.paragraph_format.space_before = Pt(6)
        p_h.paragraph_format.space_after = Pt(18)
        for r in p_h.runs:
            r.font.size = Pt(12)

        add_identity_table_block(doc, cfg)

        sp1 = doc.add_paragraph(); sp1.paragraph_format.space_after = Pt(12)
        sig_tbl = doc.add_table(rows=3, cols=2)
        sig_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        sig_tbl.autofit = False
        set_borderless_table(sig_tbl)
        p2_name = pmb.get("dosen_penilai_2", "............................................")
        p2_nip = pmb.get("nip_penilai_2", "......................................")
        p3_name = pmb.get("dosen_penilai_3", "............................................")
        p3_nip = pmb.get("nip_penilai_3", "......................................")
        sig_rows = [
            ("Dosen Penilai I / Pembimbing", "Dosen Penilai II"),
            (f"{pmb['dosen_pembimbing']}\nNIP {pmb['nip_pembimbing']}", f"{p2_name}\nNIP {p2_nip}"),
            (f"Dosen Penilai III\n\n\n{p3_name}\nNIP {p3_nip}", f"{kota}, ........................ {tahun}"),
        ]
        for r_i, (left_t, right_t) in enumerate(sig_rows):
            for c_i, txt in enumerate((left_t, right_t)):
                cell = sig_tbl.cell(r_i, c_i)
                cell.width = Cm(7.0)
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(28 if r_i == 1 else 10)
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.line_spacing = 1.0
                p.paragraph_format.first_line_indent = Cm(0)
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                for idx_l, lval in enumerate(txt.split("\n")):
                    if idx_l > 0:
                        p.add_run().add_break()
                    set_run_font(p.add_run(lval), size_pt=11)

    if skr.get("include_keaslian_page", True):
        doc.add_page_break()
        add_front_header_block(doc, cfg)
        p_k = add_judul_bab(doc, "PERNYATAAN KEASLIAN", "SKRIPSI", style_name="JUDUL AWAL")
        p_k.paragraph_format.space_before = Pt(6)
        p_k.paragraph_format.space_after = Pt(18)
        for r in p_k.runs:
            r.font.size = Pt(12)

        add_identity_table_block(doc, cfg)

        p_stmt = doc.add_paragraph()
        p_stmt.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_stmt.paragraph_format.space_before = Pt(18)
        p_stmt.paragraph_format.space_after = Pt(24)
        p_stmt.paragraph_format.line_spacing = 1.5
        p_stmt.paragraph_format.first_line_indent = Cm(1.27)
        set_run_font(p_stmt.add_run(
            "Dengan ini menyatakan bahwa sesungguhnya Skripsi ini adalah hasil tulisan penulis sendiri dan tidak terdapat bagian atau keseluruhan tulisan yang disalin atau ditiru tanpa memberikan pengakuan pada penulis aslinya. Apabila terbukti melakukan plagiarisme, penulis siap dinyatakan tidak lulus dan dicabut gelar yang telah diberikan."
        ), size_pt=12)

        p_sig = doc.add_paragraph()
        p_sig.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_sig.paragraph_format.left_indent = Cm(7.5)
        p_sig.paragraph_format.space_before = Pt(12)
        p_sig.paragraph_format.line_spacing = 1.15
        set_run_font(p_sig.add_run(f"{kota}, ........................ {tahun}"), size_pt=12)
        p_sig.add_run().add_break()
        set_run_font(p_sig.add_run("Yang memberi pernyataan,"), size_pt=12)
        for _ in range(4):
            p_sig.add_run().add_break()
        set_run_font(p_sig.add_run(mhs["nama"]), size_pt=12, bold=True)
        p_sig.add_run().add_break()
        set_run_font(p_sig.add_run(f"NPM {mhs['npm']}"), size_pt=12)


def add_kata_pengantar(doc, cfg: dict):
    doc.add_page_break()
    add_judul_bab(doc, "KATA PENGANTAR", style_name="JUDUL AWAL")
    mhs = cfg["mahasiswa"]
    skr = cfg["skripsi"]
    kota = mhs.get("kota_kampus", "Tangerang Selatan")

    p1 = doc.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p1.paragraph_format.line_spacing = 2.0; p1.paragraph_format.first_line_indent = Cm(1.27)
    set_run_font(p1.add_run(
        f"Puji dan syukur penulis panjatkan ke hadirat Tuhan Yang Maha Esa atas rahmat-Nya sehingga karya ilmiah berjudul \"{skr['judul']}\" ini dapat diselesaikan. "
        f"Skripsi ini disusun sebagai bagian dari syarat untuk meraih gelar {mhs.get('jenjang_gelar', 'Sarjana Terapan')} {mhs['prodi'].title()} pada {mhs.get('kampus', 'Politeknik Keuangan Negara STAN').title()}. "
        "Ucapan terima kasih penulis sampaikan kepada:"
    ), size_pt=12)

    for item in skr.get("kata_pengantar_items", []):
        pi = doc.add_paragraph()
        pi.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pi.paragraph_format.line_spacing = 2.0
        pi.paragraph_format.left_indent = Cm(1.90); pi.paragraph_format.first_line_indent = Cm(-0.63)
        set_run_font(pi.add_run(item), size_pt=12)

    pcl = doc.add_paragraph()
    pcl.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pcl.paragraph_format.line_spacing = 2.0; pcl.paragraph_format.first_line_indent = Cm(1.27)
    set_run_font(pcl.add_run("Semoga skripsi ini dapat memberikan manfaat bagi pengembangan ilmu pengetahuan dan praktik kebijakan keuangan publik di Indonesia."), size_pt=12)

    psig = doc.add_paragraph()
    psig.paragraph_format.left_indent = Cm(8.5); psig.paragraph_format.space_before = Pt(12); psig.paragraph_format.line_spacing = 1.5
    set_run_font(psig.add_run(f"{kota}, ........................ {mhs['tahun_lulus']}"), size_pt=12)
    for _ in range(3):
        psig.add_run().add_break()
    set_run_font(psig.add_run(mhs["nama"]), size_pt=12, bold=True)


def add_abstrak_page(doc, cfg: dict, ws_root: pathlib.Path):
    skr = cfg["skripsi"]
    abs_path = ws_root / skr.get("abstrak_file", "")
    if not abs_path.exists():
        return
    doc.add_page_break()
    add_judul_bab(doc, "ABSTRAK", style_name="JUDUL AWAL")
    abs_text = re.sub(r"^---\n.*?\n---\n+", "", abs_path.read_text(encoding="utf-8"), flags=re.S).strip()
    abs_wc = len(re.findall(r"\S+", abs_text.replace("*", "").replace("`", "")))
    if abs_wc > 250:
        print(f"[WARN] Abstract exceeds 250 words ({abs_wc} words) — PER-9/PKN/2020 Art. 3.1.1.2 limit is <= 250 words.")
    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_abs.paragraph_format.line_spacing = 1.0
    p_abs.paragraph_format.first_line_indent = Cm(1.27)
    append_non_citation_markdown(p_abs, abs_text, size_pt=12)
    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_before = Pt(6); p_kw.paragraph_format.line_spacing = 1.0
    p_kw.paragraph_format.first_line_indent = Cm(0)
    set_run_font(p_kw.add_run("Kata kunci: "), size_pt=12, bold=True)
    append_non_citation_markdown(p_kw, skr.get("kata_kunci", ""), size_pt=12)


def count_list_items(cfg: dict, mode: str, ws_root: pathlib.Path) -> tuple[int, int, int]:
    max_ch = 3 if mode == "proposal" else 5
    n_tbl, n_fig = 0, 0
    for ch in cfg["paths"].get("chapters", []):
        if ch["num"] > max_ch:
            continue
        p = ws_root / ch["md"]
        if not p.exists():
            continue
        for ln in p.read_text(encoding="utf-8").splitlines():
            s = ln.strip()
            if re.match(r"^Tabel\s+[IVX]+\.\d+\b", s):
                n_tbl += 1
            elif re.match(r"^Gambar\s+[IVX]+\.\d+\b", s):
                n_fig += 1
    app_key = "proposal_appendices" if mode == "proposal" else "appendices"
    n_app = sum(1 for a in cfg["paths"].get(app_key, []) if (ws_root / a.get("md", "")).exists())
    return n_tbl, n_fig, n_app


def add_toc_pages(doc, cfg: dict, mode: str, ws_root: pathlib.Path):
    n_tbl, n_fig, n_app = count_list_items(cfg, mode, ws_root)
    force_all = cfg.get("skripsi", {}).get("always_include_lists", False)
    min_req = 3

    toc_specs = [
        ("DAFTAR ISI", ' TOC \\h \\z \\t "JUDUL AWAL,1,JUDUL BAB,1,Judul Subbab,2,Judul Bagian Subbab,3" '),
    ]
    if force_all or (mode == "thesis" and n_tbl >= min_req) or (mode == "proposal" and n_tbl >= min_req):
        toc_specs.append(("DAFTAR TABEL", ' TOC \\h \\z \\t "Tabel,1" '))
    if force_all or (mode == "thesis" and n_fig >= min_req) or (mode == "proposal" and n_fig >= min_req):
        toc_specs.append(("DAFTAR GAMBAR", ' TOC \\h \\z \\t "Gambar,1" '))
    if force_all or (mode == "thesis" and n_app >= min_req) or (mode == "proposal" and n_app >= min_req):
        toc_specs.append(("DAFTAR LAMPIRAN", ' TOC \\h \\z \\t "Lampiran,1" '))

    for title, instr in toc_specs:
        doc.add_page_break()
        add_judul_bab(doc, title, style_name="JUDUL AWAL")
        p = doc.add_paragraph()
        p.style = doc.styles["toc 1"]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        add_field(p, instr, "Memperbarui daftar...", size_pt=12)


def add_booktabs_table(doc, rows_md, widths_cm, cit_engine: CitationEngine):
    n_rows, n_cols = len(rows_md), len(rows_md[0])
    if not widths_cm or len(widths_cm) != n_cols:
        widths_cm = [round(14.0 / n_cols, 2)] * n_cols
    tbl = doc.add_table(rows=n_rows, cols=n_cols)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tblPr = tbl._tbl.tblPr
    old_b = tblPr.find(qn("w:tblBorders"))
    if old_b is not None:
        tblPr.remove(old_b)
    insert_xsd_order(
        tblPr,
        parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            '<w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
            '<w:left w:val="none"/><w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
            '<w:right w:val="none"/><w:insideH w:val="none"/><w:insideV w:val="none"/>'
            '</w:tblBorders>'
        ),
        XSD_TBLPR_ORDER,
    )
    font_pt = 8.5 if n_cols >= 7 else 9.5 if n_cols >= 5 else 10.0
    for r_i, row_data in enumerate(rows_md):
        is_hdr = r_i == 0
        trPr = tbl.rows[r_i]._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
        if is_hdr:
            trPr.append(OxmlElement("w:tblHeader"))
        for c_i, cell_txt in enumerate(row_data):
            cell = tbl.cell(r_i, c_i)
            cell.width = Cm(widths_cm[c_i])
            if is_hdr:
                tcPr = cell._tc.get_or_add_tcPr()
                insert_xsd_order(
                    tcPr,
                    parse_xml(f'<w:tcBorders {nsdecls("w")}><w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/></w:tcBorders>'),
                    ("tcW", "gridSpan", "hMerge", "vMerge", "tcBorders"),
                )
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0; p.paragraph_format.first_line_indent = Cm(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if (is_hdr or c_i == 0) else WD_ALIGN_PARAGRAPH.LEFT
            cit_engine.append_rich_line(p, cell_txt.strip(), size_pt=font_pt, base_bold=is_hdr)


def add_seq_caption(doc, style_name, prefix_text, seq_name, title_md):
    p = doc.add_paragraph()
    p.style = doc.styles[style_name]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT if style_name == "Lampiran" else WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.keep_with_next = True
    sz = 12 if style_name == "Lampiran" else 11
    set_run_font(p.add_run(prefix_text), size_pt=sz, bold=True)
    add_field(p, f" SEQ {seq_name} \\* ARABIC ", "1", size_pt=sz, bold=True)
    set_run_font(p.add_run(" "), size_pt=sz, bold=True)
    append_non_citation_markdown(p, title_md, size_pt=sz, base_bold=True)
    return p


def render_markdown_body(doc, raw_md: str, cfg: dict, cit_engine: CitationEngine, ws_root: pathlib.Path) -> None:
    body = re.sub(r"^---\n.*?\n---\n+", "", raw_md, flags=re.S)
    lines = body.splitlines()
    fig_map = cfg["paths"].get("figures", {})
    col_map = cfg["paths"].get("table_col_widths", {})

    heading_style_map = [
        ("##### ", "Jusul Subbagian bagian-subbab", False),
        ("#### ", "Judul Bagian Bagian-Subbab", False),
        ("### ", "Judul Bagian Subbab", True),
        ("## ", "Judul Subbab", True),
    ]

    i = 0
    in_code = False
    active_tbl_num = None
    skip_next_fig_md = False
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        if s.startswith("```"):
            in_code = not in_code
            i += 1
            continue
        if in_code or s.startswith("# BAB ") or s.startswith("# Lampiran"):
            i += 1
            continue

        matched_heading = False
        for prefix_h, st_name, is_bold_h in heading_style_map:
            if s.startswith(prefix_h):
                clean_h = re.sub(r"^\d+(?:\.\d+)+\s+", "", s[len(prefix_h):].strip())
                p = doc.add_paragraph()
                p.style = doc.styles[st_name]
                p.paragraph_format.keep_with_next = True
                append_non_citation_markdown(p, clean_h, size_pt=12, base_bold=is_bold_h)
                matched_heading = True
                break
        if matched_heading:
            skip_next_fig_md = False
            i += 1
            continue

        # Blockquote -> Long Direct Quote (Kutipan Langsung: 1.0 spacing, 1.27cm left/right indent)
        if s.startswith("> "):
            skip_next_fig_md = False
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].strip().lstrip(">").strip())
                i += 1
            p = doc.add_paragraph()
            p.style = doc.styles["Kutipan Langsung"]
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.left_indent = Cm(1.27)
            p.paragraph_format.right_indent = Cm(1.27)
            p.paragraph_format.first_line_indent = Cm(0)
            cit_engine.append_rich_line(p, " ".join(quote_lines), size_pt=12)
            continue

        eq_m = re.match(r"^\$\$(.+?)\$\$\s+\((\d+\.\d+)\)$", s)
        if eq_m:
            skip_next_fig_md = False
            tbl = doc.add_table(rows=1, cols=2)
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            tbl.autofit = False
            set_borderless_table(tbl)
            c0, c1 = tbl.cell(0, 0), tbl.cell(0, 1)
            c0.width, c1.width = Cm(12.6), Cm(1.4)
            p0, p1 = c0.paragraphs[0], c1.paragraphs[0]
            p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            set_run_font(p0.add_run(eq_m.group(1).strip()), size_pt=12, italic=True)
            set_run_font(p1.add_run(f"({eq_m.group(2)})"), size_pt=12)
            i += 1
            continue

        tbl_m = re.match(r"^Tabel\s+([IVX]+)\.(\d+)\s+(.*)$", s)
        if tbl_m:
            skip_next_fig_md = False
            rom, num, title_rest = tbl_m.groups()
            active_tbl_num = f"{rom}.{num}"
            add_seq_caption(doc, "Tabel", f"Tabel {rom}.", f"Tabel_{rom}", title_rest)
            i += 1
            continue

        if s.startswith("|"):
            skip_next_fig_md = False
            rows_md = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rs = lines[i].strip()
                if re.fullmatch(r"\|[\s:\-|]+\|", rs):
                    i += 1
                    continue
                rows_md.append([c.strip().replace("\\|", "/") for c in re.split(r"(?<!\\)\|", rs.strip("|"))])
                i += 1
            if rows_md:
                add_booktabs_table(doc, rows_md, col_map.get(active_tbl_num or "", []), cit_engine)
            continue

        fig_m = re.match(r"^Gambar\s+([IVX]+)\.(\d+)\s+(.*)$", s)
        if fig_m:
            rom, num, title_rest = fig_m.groups()
            fkey = f"{rom}.{num}"
            add_seq_caption(doc, "Gambar", f"Gambar {rom}.", f"Gambar_{rom}", title_rest)
            if fkey in fig_map and (ws_root / fig_map[fkey]).exists():
                p_img = doc.add_paragraph()
                p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_img.paragraph_format.keep_with_next = True
                p_img.add_run().add_picture(str(ws_root / fig_map[fkey]), width=Cm(14.0))
                skip_next_fig_md = True
            else:
                skip_next_fig_md = False
            i += 1
            continue

        img_m = re.match(r"^!\[(.*?)\]\((.+?)\)$", s)
        if img_m:
            if skip_next_fig_md:
                skip_next_fig_md = False
                i += 1
                continue
            img_path = ws_root / img_m.group(2)
            if img_path.exists():
                p_img = doc.add_paragraph()
                p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_img.paragraph_format.keep_with_next = True
                p_img.add_run().add_picture(str(img_path), width=Cm(14.0))
            i += 1
            continue

        skip_next_fig_md = False

        if s.startswith("Sumber:") or s.startswith("Catatan:"):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY if (s.startswith("Catatan:") or len(s) > 95) else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(4); p.paragraph_format.space_after = Pt(12)
            p.paragraph_format.line_spacing = 1.0; p.paragraph_format.first_line_indent = Cm(0)
            cit_engine.append_rich_line(p, s, size_pt=10)
            i += 1
            continue

        if s.startswith("- ") or re.match(r"^\d+\.\s+", s):
            is_bullet = s.startswith("- ")
            txt_item = ("•  " + s[2:].strip()) if is_bullet else s
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = 2.0
            p.paragraph_format.left_indent = Cm(1.90); p.paragraph_format.first_line_indent = Cm(-0.63)
            cit_engine.append_rich_line(p, txt_item, size_pt=12)
            i += 1
            continue

        p = doc.add_paragraph()
        p.style = doc.styles["~normal"]
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 2.0; p.paragraph_format.first_line_indent = Cm(1.27)
        cit_engine.append_rich_line(p, s, size_pt=12)
        i += 1


def render_chapter(doc, ch_cfg: dict, cfg: dict, cit_engine: CitationEngine, ws_root: pathlib.Path, is_first=False):
    md_path = ws_root / ch_cfg["md"]
    if not md_path.exists():
        raise FileNotFoundError(f"Chapter Markdown file not found: {md_path}")

    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    configure_chapter_section(sec, start_decimal=1 if is_first else None, first_page_bottom=True)
    add_top_spacer(doc)
    add_judul_bab(doc, ch_cfg["label"], ch_cfg["title"])
    render_markdown_body(doc, md_path.read_text(encoding="utf-8"), cfg, cit_engine, ws_root)


class BibHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.segments, self.italic, self.bold = [], False, False

    def handle_starttag(self, tag, attrs):
        if tag in ("i", "em"):
            self.italic = True
        elif tag in ("b", "strong"):
            self.bold = True

    def handle_endtag(self, tag):
        if tag in ("i", "em"):
            self.italic = False
        elif tag in ("b", "strong"):
            self.bold = False

    def handle_data(self, data):
        if data:
            self.segments.append((data, self.bold, self.italic))


def add_daftar_pustaka(doc, cfg: dict, zmap: dict, cited_keys: list[str]):
    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    configure_chapter_section(sec, start_decimal=None, first_page_bottom=True)
    add_top_spacer(doc)
    add_judul_bab(doc, "DAFTAR PUSTAKA", style_name="JUDUL AWAL")

    keys = cited_keys or list(zmap.get("items", {}).keys())
    uid = cfg.get("zotero", {}).get("user_id", "0")
    locale = cfg.get("zotero", {}).get("locale", "id-ID")
    bib_runs_list = []
    if keys:
        try:
            url = f"http://127.0.0.1:23119/api/users/{uid}/items?itemKey={','.join(keys)}&format=bib&style=apa&locale={locale}"
            with urllib.request.urlopen(urllib.request.Request(url), timeout=4) as resp:
                entries = [m.strip() for m in re.findall(r'<div class="csl-entry">(.*?)</div>', resp.read().decode("utf-8"), re.S)]
            for eh in entries:
                p = BibHTMLParser()
                p.feed(html.unescape(eh))
                bib_runs_list.append(p.segments)
        except Exception:
            for k in keys:
                it = zmap.get("items", {}).get(k, {})
                title = it.get("title", k)
                yr = str(it.get("issued", {}).get("date-parts", [[""]])[0][0])
                bib_runs_list.append([(f"{title} ({yr}).", False, False)])

    if not bib_runs_list:
        p = doc.add_paragraph()
        set_run_font(p.add_run("[Klik Zotero -> Refresh di Microsoft Word untuk memunculkan Daftar Pustaka otomatis.]"), size_pt=12)
        return

    for idx, segs in enumerate(bib_runs_list):
        bp = doc.add_paragraph()
        bp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        bp.paragraph_format.left_indent = Cm(1.27); bp.paragraph_format.first_line_indent = Cm(-1.27)
        bp.paragraph_format.line_spacing = 1.0; bp.paragraph_format.space_after = Pt(12)
        if idx == 0:
            add_fld_char(bp, "begin", size_pt=12)
            add_instr_text(bp, ' ADDIN ZOTERO_BIBL {"uncited":[],"omitted":[],"custom":[]} CSL_BIBLIOGRAPHY ', size_pt=12)
            add_fld_char(bp, "separate", size_pt=12)
        for txt, is_b, is_i in segs:
            set_run_font(bp.add_run(txt), size_pt=12, bold=is_b, italic=is_i)
        if idx == len(bib_runs_list) - 1:
            add_fld_char(bp, "end", size_pt=12)


def add_appendices_section(doc, cfg: dict, mode: str, cit_engine: CitationEngine, ws_root: pathlib.Path):
    app_key = "proposal_appendices" if mode == "proposal" else "appendices"
    apps = cfg["paths"].get(app_key, [])
    existing = [a for a in apps if (ws_root / a.get("md", "")).exists()]
    if not existing:
        return
    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    configure_chapter_section(sec, start_decimal=None, first_page_bottom=True)
    for idx, app in enumerate(existing):
        if idx > 0:
            doc.add_page_break()
        if idx == 0:
            add_top_spacer(doc)
        add_seq_caption(doc, "Lampiran", "Lampiran ", "Lampiran", app.get("title", "Lampiran Pendukung"))
        md_txt = (ws_root / app["md"]).read_text(encoding="utf-8")
        render_markdown_body(doc, md_txt, cfg, cit_engine, ws_root)


def add_daftar_riwayat_hidup(doc, cfg: dict):
    drh = cfg.get("riwayat_hidup")
    if not drh or not drh.get("enabled", False):
        return
    mhs = cfg["mahasiswa"]
    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    configure_chapter_section(sec, start_decimal=None, first_page_bottom=True)
    add_top_spacer(doc)
    add_judul_bab(doc, "DAFTAR RIWAYAT HIDUP", style_name="JUDUL AWAL")

    bio = [
        ("Nama", ":", mhs["nama"]),
        ("Tempat, Tanggal Lahir", ":", drh.get("ttl", "[Tempat, Tanggal Lahir]")),
        ("Jenis Kelamin", ":", drh.get("jenis_kelamin", "[Laki-Laki / Perempuan]")),
        ("Alamat", ":", drh.get("alamat", "[Alamat Lengkap]")),
        ("Kontak", ":", drh.get("kontak", "[Nomor HP / Email]")),
    ]
    tbl_b = doc.add_table(rows=len(bio), cols=3)
    tbl_b.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_b.autofit = False
    set_borderless_table(tbl_b)
    for r_i, (k, sep, v) in enumerate(bio):
        for c_i, (val, cw) in enumerate(zip((k, sep, v), (Cm(4.8), Cm(0.5), Cm(8.7)))):
            cell = tbl_b.cell(r_i, c_i)
            cell.width = cw
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2); p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.25; p.paragraph_format.first_line_indent = Cm(0)
            set_run_font(p.add_run(val), size_pt=12)

    edu = drh.get("pendidikan", [])
    if edu:
        p_edu = doc.add_paragraph()
        p_edu.paragraph_format.space_before = Pt(14); p_edu.paragraph_format.space_after = Pt(6)
        p_edu.paragraph_format.first_line_indent = Cm(0)
        set_run_font(p_edu.add_run("Riwayat Pendidikan:"), size_pt=12, bold=True)
        edu_rows = [["Jenjang / Institusi Pendidikan", "Tahun Kelulusan"]] + [[e[0], str(e[1])] for e in edu]
        add_booktabs_table(doc, edu_rows, [10.5, 3.5], CitationEngine({}, []))

    org = drh.get("organisasi", [])
    if org:
        p_org = doc.add_paragraph()
        p_org.paragraph_format.space_before = Pt(14); p_org.paragraph_format.space_after = Pt(6)
        p_org.paragraph_format.first_line_indent = Cm(0)
        set_run_font(p_org.add_run("Riwayat Organisasi:"), size_pt=12, bold=True)
        org_rows = [["Nama Organisasi", "Posisi", "Tahun"]] + [[o[0], o[1], str(o[2])] for o in org]
        add_booktabs_table(doc, org_rows, [7.2, 4.3, 2.5], CitationEngine({}, []))


ARCHETYPE_TITLES = {
    "descriptive_simulation": (
        "INTI PENELITIAN",
        "HASIL PENELITIAN DAN EVALUASI",
    ),
    "deskriptif_simulasi": (
        "INTI PENELITIAN",
        "HASIL PENELITIAN DAN EVALUASI",
    ),
    "descriptive_design": (
        "ANALISIS SISTEM YANG BERJALAN",
        "RANCANGAN SISTEM YANG DIUSULKAN",
    ),
    "deskriptif_desain": (
        "ANALISIS SISTEM YANG BERJALAN",
        "RANCANGAN SISTEM YANG DIUSULKAN",
    ),
}


def apply_archetype_chapter_titles(cfg: dict) -> None:
    arch = str(cfg.get("skripsi", {}).get("archetype", "quantitative")).strip().lower()
    if arch not in ARCHETYPE_TITLES:
        return
    t3, t4 = ARCHETYPE_TITLES[arch]
    for ch in cfg.get("paths", {}).get("chapters", []):
        if ch.get("num") == 3 and ch.get("title") in ("METODE PENELITIAN", ""):
            ch["title"] = t3
        elif ch.get("num") == 4 and ch.get("title") in ("HASIL PENELITIAN DAN PEMBAHASAN", ""):
            ch["title"] = t4


def main():
    parser = argparse.ArgumentParser(description="Build Proposal or Complete Thesis DOCX from Markdown + Config.")
    parser.add_argument("--config", type=pathlib.Path, required=True, help="Path to thesis_config.json")
    parser.add_argument("--mode", choices=["proposal", "thesis", "skripsi"], default="thesis")
    args = parser.parse_args()
    mode = "thesis" if args.mode in ("thesis", "skripsi") else "proposal"

    cfg_path = args.config.resolve()
    ws_root = cfg_path.parent
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    apply_archetype_chapter_titles(cfg)

    zmap_path = ws_root / cfg["zotero"]["map_file"]
    specs_path = ws_root / cfg["zotero"]["citation_specs_file"]
    zmap = json.loads(zmap_path.read_text(encoding="utf-8")) if zmap_path.exists() else {}
    if specs_path.exists():
        specs = json.loads(specs_path.read_text(encoding="utf-8"))
    elif zmap.get("items"):
        import sys as _sys
        _sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
        from generate_citation_specs import generate_specs_from_texts

        _texts = []
        for _kl in ("chapters", "proposal_appendices", "appendices"):
            for _en in cfg["paths"].get(_kl, []):
                _p = ws_root / _en.get("md", "")
                if _p.exists():
                    _texts.append(_p.read_text(encoding="utf-8"))
        specs, _unmatched = generate_specs_from_texts(_texts, zmap)
        if specs:
            specs_path.parent.mkdir(parents=True, exist_ok=True)
            specs_path.write_text(json.dumps(specs, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"AUTO-ZOTERO: Matched {len(specs)} citation patterns -> {specs_path.name}")
    else:
        specs = []
    cit_engine = CitationEngine(zmap, specs)

    tmp_tpl = ws_root / "04. Output DOCX" / f"_base_{mode}.docx"
    prepare_base_template(cfg, mode, tmp_tpl, ws_root)
    doc = Document(str(tmp_tpl))

    sec0 = doc.sections[0]
    sec0.different_first_page_header_footer = True
    clear_hf(sec0.header); clear_hf(sec0.footer)
    clear_hf(sec0.first_page_header); clear_hf(sec0.first_page_footer)

    configure_front_section(doc.sections[1], start_roman=2)
    if mode == "thesis":
        add_lulus_and_keaslian_pages(doc, cfg)
        add_kata_pengantar(doc, cfg)
    add_toc_pages(doc, cfg, mode, ws_root)
    if mode == "thesis":
        add_abstrak_page(doc, cfg, ws_root)

    max_ch = 3 if mode == "proposal" else 5
    chapters = [c for c in cfg["paths"]["chapters"] if c["num"] <= max_ch]
    for ch in chapters:
        render_chapter(doc, ch, cfg, cit_engine, ws_root, is_first=(ch["num"] == 1))

    add_daftar_pustaka(doc, cfg, zmap, cit_engine.emitted_keys)
    add_appendices_section(doc, cfg, mode, cit_engine, ws_root)
    if mode == "thesis":
        add_daftar_riwayat_hidup(doc, cfg)

    out_key = "output_proposal_docx" if mode == "proposal" else "output_skripsi_docx"
    out_path = ws_root / cfg["paths"][out_key]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))
    if tmp_tpl.exists():
        tmp_tpl.unlink()
    print(f"OK: Built {mode.upper()} DOCX -> {out_path} ({len(cit_engine.emitted_keys)} Zotero items)")


if __name__ == "__main__":
    main()
