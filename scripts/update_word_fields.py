"""Update all Word TOC, SEQ, PAGE fields via Microsoft Word COM on Windows."""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import tempfile


def update_word_fields(docx_path: pathlib.Path) -> None:
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
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps_path)],
            capture_output=True,
            text=True,
            check=True,
        )
        print(res.stdout.strip())
    finally:
        ps_path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh Word TOC/SEQ/PAGE fields via Microsoft Word COM.")
    parser.add_argument("docx", type=pathlib.Path, help="Path to built .docx file")
    args = parser.parse_args()
    update_word_fields(args.docx)


if __name__ == "__main__":
    main()
