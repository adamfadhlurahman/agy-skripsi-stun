"""Zero-dependency environment & ecosystem readiness checker for AGY Thesis Starter Kit."""

from __future__ import annotations

import importlib
import json
import pathlib
import platform
import sys
import urllib.request


CORE_PACKAGES = [
    ("docx", "python-docx"),
    ("lxml", "lxml"),
    ("pymupdf", "pymupdf"),
    ("pypdf", "pypdf"),
    ("openpyxl", "openpyxl"),
    ("matplotlib", "matplotlib"),
]

OPTIONAL_DATA_PACKAGES = [
    ("pandas", "pandas"),
    ("statsmodels", "statsmodels"),
    ("scipy", "scipy"),
]


def check_zotero_local_api() -> tuple[bool, str]:
    url = "http://127.0.0.1:23119/api/users/0/collections?limit=5"
    try:
        with urllib.request.urlopen(urllib.request.Request(url), timeout=2) as resp:
            if resp.status == 200:
                cols = json.loads(resp.read().decode("utf-8"))
                return True, f"Active ({len(cols)} collections detected)"
    except Exception as exc:
        return False, f"Not running / Zotero Desktop closed ({exc.__class__.__name__})"
    return False, "No response"


def main() -> None:
    root = pathlib.Path(__file__).resolve().parent.parent
    print("=== AGY THESIS STARTER KIT (STUN EDITION) READINESS CHECK ===")
    print(f"Python   : {platform.python_version()} ({sys.executable})")
    print(f"Workspace: {root}")

    missing_core: list[str] = []
    print("\n1. Required Python Packages:")
    for mod, pkg in CORE_PACKAGES:
        try:
            importlib.import_module(mod)
            print(f"   [OK]      {pkg}")
        except ImportError:
            missing_core.append(pkg)
            print(f"   [MISSING] {pkg}")

    print("\n2. Optional Data Analysis Packages:")
    for mod, pkg in OPTIONAL_DATA_PACKAGES:
        try:
            importlib.import_module(mod)
            print(f"   [OK]      {pkg}")
        except ImportError:
            print(f"   [OPT]     {pkg} (install later if using Python for data analysis)")

    zot_ok, zot_msg = check_zotero_local_api()
    print(f"\n3. Zotero Desktop Local API : {'[OK]' if zot_ok else '[INFO]'} {zot_msg}")

    skills_dir = root / ".agents" / "skills"
    skills = sorted(d.name for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()) if skills_dir.exists() else []
    print(f"4. Bundled Local Skills     : {len(skills)} active skills ({', '.join(skills)})")

    cfg_exists = (root / "thesis_config.json").exists()
    print(f"5. Configuration File       : {'thesis_config.json found' if cfg_exists else 'Not created yet (auto-created in Phase 0)'}")

    voice_exists = (root / ".agents" / "skills" / "humanizer-indonesia" / "references" / "voice-penulis-id.md").exists()
    print(f"6. Author Voice Profile     : {'Calibrated (voice-penulis-id.md found)' if voice_exists else '[INFO] Not calibrated yet (will be created in Phase 3)'}")

    if missing_core:
        print(f"\nACTION: Run 'pip install {' '.join(missing_core)}' or 'powershell -ExecutionPolicy Bypass -File scripts/setup.ps1'")
        sys.exit(1)
    print("\nSTATUS: All core components are ready.")


if __name__ == "__main__":
    main()
