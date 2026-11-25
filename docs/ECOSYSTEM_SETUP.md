# Research Ecosystem Setup (Built-In & Optional Add-Ons)

## 1. What Works Out of the Box (From ZIP Alone, Zero MCP Needed)?

This starter kit **works immediately right after extracting the ZIP**—no manual plugin or external MCP installation required:

* **16 Local Skills Bundled Inside `.agents/skills/`:**
  * **PKN STAN Orchestration & Standards:** `thesis-autopilot`, `pkn-stan-thesis-writer`, `humanizer-indonesia` (+ `scripts/metrik.py`)
  * **Ideation & Gap Testing:** `research-ideation`, `gap-to-topic`, `research-design-helper`
  * **Literature & Peer Review:** `lit-review-assistant`, `literature-triage-matrix`, `paper-summarize`, `paper-review`
  * **Data Analysis & Publication Figures:** `working-with-data`, `python-panel-data`, `r-econometrics`, `stata-data-cleaning`, `stata-regression`, `econ-visualization`
* **Built-In Academic Paper Search (`scripts/search_papers.py`):** Uses Python's standard library to query **OpenAlex & CrossRef** (no API key or MCP required), verify real DOIs/citation counts/abstracts, download legal Open Access PDFs directly to `01. Literature/`, and export CSL-JSON to `03. Drafts/zotero_map.json`.

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

## 4. Optional MCP Servers (Extra Research Power for Advanced Users)

Even **without any MCP server**, your AI agent can already find real peer-reviewed papers via `scripts/search_papers.py` (OpenAlex & CrossRef), search regulations via web search, and read local PDFs in `01. Literature/`.

If you want extra direct API integrations inside Antigravity (`~/.gemini/config/mcp_config.json`) or Claude Code (`.mcp.json`), you may optionally install these external MCP servers later:

1. **`paper-search`** (`https://github.com/openags/paper-search-mcp`) — Extended multi-database search (arXiv, Semantic Scholar, CrossRef, OpenAlex, PubMed, SSRN).
2. **`zotero`** (`https://github.com/54yyyu/zotero-mcp`) — Read/write Zotero collections, items, tags, and annotations directly from chat.
3. **`openecon-data`** / **`notebooklm-mcp`** — Optional macro-economic time-series API and NotebookLM cross-document Q&A (requires external MCP installation/auth).
