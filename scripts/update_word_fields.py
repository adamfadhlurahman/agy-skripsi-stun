"""Update all Word TOC, SEQ, PAGE fields via Microsoft Word COM on Windows (graceful skip on non-Windows)."""

from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from lxml import etree


def _sync_core_author(docx_path: pathlib.Path, author_override: str | None = None) -> None:
    """Keep Last Modified By aligned with Author (student name) after Word COM Save()."""
    if not docx_path.exists():
        return
    dc_ns = "http://purl.org/dc/elements/1.1/"
    cp_ns = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
    dt_ns = "http://purl.org/dc/terms/"
    with zipfile.ZipFile(docx_path, "r") as zin:
        if "docProps/core.xml" not in zin.namelist():
            return
        items = {item.filename: (item, zin.read(item.filename)) for item in zin.infolist()}
    core_root = etree.fromstring(items["docProps/core.xml"][1])
    creator_el = core_root.find(f"{{{dc_ns}}}creator")
    target_author = (author_override or (creator_el.text if creator_el is not None else "") or "").strip()
    if not target_author:
        return
    if creator_el is not None:
        creator_el.text = target_author
    lmb_el = core_root.find(f"{{{cp_ns}}}lastModifiedBy")
    if lmb_el is not None:
        lmb_el.text = target_author
    mod_el = core_root.find(f"{{{dt_ns}}}modified")
    if mod_el is not None:
        mod_el.text = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    new_core = etree.tostring(core_root, xml_declaration=True, encoding="UTF-8", standalone=True)
    tmp_out = docx_path.with_suffix(".tmp.docx")
    with zipfile.ZipFile(tmp_out, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for fname, (info, data) in items.items():
            zout.writestr(fname if fname == "docProps/core.xml" else info, new_core if fname == "docProps/core.xml" else data)
    tmp_out.replace(docx_path)


def update_word_fields(docx_path: pathlib.Path, author_override: str | None = None) -> None:
    if sys.platform != "win32" or not (shutil.which("powershell") or shutil.which("pwsh")):
        print(
            "[INFO] Automatic Word field update (Word COM) is only available on Windows with Microsoft Word Desktop. "
            f"Open {docx_path.name} in Microsoft Word and press Select All -> F9 (or Update Field) to refresh page numbers."
        )
        return
    shell_exe = shutil.which("powershell") or shutil.which("pwsh") or "powershell"
    docx_abs = str(docx_path.resolve())
    ps_script = f'''
$ErrorActionPreference = "Stop"
$path = "{docx_abs}"
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$doc = $null
try {{
    $doc = $word.Documents.Open($path)
    $doc.Repaginate()
    $doc.Fields.Update() | Out-Null
    foreach ($toc in $doc.TablesOfContents) {{ $toc.Update() }}
    foreach ($sec in $doc.Sections) {{
        foreach ($hf in $sec.Headers) {{ $hf.Range.Fields.Update() | Out-Null }}
        foreach ($hf in $sec.Footers) {{ $hf.Range.Fields.Update() | Out-Null }}
    }}
    $doc.Repaginate()
    $doc.Save()
    Write-Output ("WORD_COM_OK: Pages=" + $doc.ComputeStatistics(2) + " Words=" + $doc.ComputeStatistics(0) + " TOCs=" + $doc.TablesOfContents.Count)
}} finally {{
    if ($doc -ne $null) {{ $doc.Close([ref]$false) }}
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
}}
'''
    with tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False, encoding="utf-8") as tf:
        tf.write(ps_script)
        ps_path = pathlib.Path(tf.name)
    try:
        res = subprocess.run(
            [shell_exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode != 0:
            print(
                "[INFO] Word COM field refresh skipped (Microsoft Word Desktop unavailable or busy). "
                f"Open {docx_path.name} in Word and press Ctrl+A -> F9 manually."
            )
            if res.stderr.strip():
                print(f"       Detail: {res.stderr.strip().splitlines()[0]}")
            return
        print(res.stdout.strip())
        _sync_core_author(docx_path, author_override=author_override)
    finally:
        ps_path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh Word TOC/SEQ/PAGE fields via Microsoft Word COM.")
    parser.add_argument("docx", type=pathlib.Path, help="Path to built .docx file")
    parser.add_argument("--author", default=None, help="Optional author override for core.xml metadata")
    args = parser.parse_args()
    update_word_fields(args.docx, author_override=args.author)


if __name__ == "__main__":
    main()
