# Research Ecosystem Setup (Built-In & Optional Add-Ons)

## 1. What Works Out of the Box?

This starter kit **bundles 16 local skills directly** inside `.agents/skills/`, so they work immediately when you open the folder in Antigravity—no manual plugin installation required:

* **PKN STAN Orchestration & Standards:** `thesis-autopilot`, `pkn-stan-thesis-writer`, `humanizer-indonesia` (+ `scripts/metrik.py`)
* **Ideation & Gap Testing:** `research-ideation`, `gap-to-topic`, `research-design-helper`
* **Literature & Peer Review:** `lit-review-assistant`, `literature-triage-matrix`, `paper-summarize`, `paper-review`
* **Data Analysis & Publication Figures:** `working-with-data`, `python-panel-data`, `r-econometrics`, `stata-data-cleaning`, `stata-regression`, `econ-visualization`

---

## 2. Required Python Packages (One-Time Install)

Run the one-click setup script (or ask AGY to run it for you):

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
```

Or manually:

```powershell
pip install -r requirements.txt
python scripts/setup_check.py
```

---

## 3. Zotero Desktop (Required for Live Word Citations)

1. Install **Zotero Desktop** and the **Zotero Word Plugin**.
2. Open Zotero Desktop -> **Settings / Preferences -> Advanced -> General**.
3. Check **"Allow other applications on this computer to communicate with Zotero"** (enables Local API on `http://127.0.0.1:23119`).
4. Create one dedicated collection for your thesis (e.g., `Thesis`), then run `scripts/setup_check.py` to confirm connectivity.

---

## 4. Optional MCP Servers (Extra Research Power)

If you want AGY to search and download journal PDFs directly or cross-check facts against NotebookLM from chat, you can add these MCP servers to your global AGY config (`~/.gemini/config/mcp_config.json`):

1. **`paper-search`** (`https://github.com/openags/paper-search-mcp`) — Search & download PDFs from arXiv, Semantic Scholar, CrossRef, OpenAlex, SSRN, etc.
2. **`zotero`** (`https://github.com/54yyyu/zotero-mcp`) — Read/write Zotero collections, items, tags, and annotations from chat.
3. **`notebooklm-mcp`** — Upload key PDFs to NotebookLM for cross-document Q&A and verification.
4. **`openecon-data`** — Query macroeconomic and financial time series (FRED, World Bank, IMF, etc.).

*(Even without external MCP servers, AGY can still search via web search and work fully with PDFs stored in `01. Literature/`.)*
