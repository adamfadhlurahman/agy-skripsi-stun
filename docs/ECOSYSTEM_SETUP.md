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

## 3. Hybrid Citation Manager Setup (Zotero OR Mendeley)

This starter kit supports **both Zotero and Mendeley** (plus a zero-manager APA 7th fallback):

### Option A — Zotero Desktop (Live Word Fields)
1. Install **Zotero Desktop** and the **Zotero Word Plugin**.
2. Open Zotero Desktop -> **Settings / Preferences -> Advanced -> General**.
3. Check **"Allow other applications on this computer to communicate with Zotero"** (enables Local API on `http://127.0.0.1:23119`).
4. Create one dedicated collection for your thesis (e.g., `Thesis`), then run `scripts/setup_check.py` to confirm connectivity.

### Option B — Mendeley (Mendeley Reference Manager / Mendeley Desktop)
1. **Store or export references:**
   - **Legacy Mendeley Desktop (unencrypted local SQLite):** Ask your agent to read your local Mendeley Desktop database directly with zero manual export:
     ```powershell
     python scripts/build_zotero_map.py --mendeley-local --collection-name "Skripsi" --out "03. Drafts/zotero_map.json"
     ```
   - **Modern Mendeley Reference Manager (or encrypted Desktop builds):** Export your Mendeley collection as **BibTeX (`.bib`)** or **RIS (`.ris`)**, then run:
     ```powershell
     python scripts/build_zotero_map.py --bib "01. Literature/library.bib" --provider mendeley --out "03. Drafts/zotero_map.json"
     ```
     *(And use `scripts/search_papers.py --export-ris "01. Literature/references_mendeley.ris"` for 1-click import into Mendeley).*
2. `build_thesis_docx.py` automatically matches every in-text APA 7th citation against your Mendeley library and builds an alphabetically sorted `DAFTAR PUSTAKA` cleanly without broken Zotero field codes. *(Modern `Mendeley Cite` for Word 365 uses private Elsevier cloud Content Controls, so offline `.docx` generation outputs clean APA 7th text & bibliography matching your Mendeley library).*

---

## 4. Optional MCP Servers (Extra Research Power for Advanced Users)

Even **without any MCP server**, your AI agent can already find real peer-reviewed papers via `scripts/search_papers.py` (OpenAlex & CrossRef), search regulations via web search, and read local PDFs in `01. Literature/`.

If you want direct cloud/chat integrations inside Antigravity (`~/.gemini/config/mcp_config.json`) or Claude Code (`.mcp.json`), you may optionally install these open-source MCP servers:

1. **`paper-search`** (`https://github.com/openags/paper-search-mcp`) — Extended multi-database search (arXiv, Semantic Scholar, CrossRef, OpenAlex, PubMed, SSRN).
2. **`zotero`** (`https://github.com/54yyyu/zotero-mcp`) — Read/write Zotero collections, items, tags, and annotations directly from chat.
3. **`mendeley-mcp`** (`https://github.com/pallaprolus/mendeley-mcp`, MIT License) — Read/write Mendeley Reference Manager collections, abstracts, highlights, and BibTeX exports directly from chat (`uv tool install mendeley-mcp`; requires registering an OAuth app at `https://dev.mendeley.com/myapps.html` with `http://localhost:8585/callback` to obtain `MENDELEY_CLIENT_ID`, `MENDELEY_CLIENT_SECRET`, and `MENDELEY_REFRESH_TOKEN`). Example snippet for `mcp_config.json`:
   ```json
   "mendeley": {
     "command": "uvx",
     "args": ["mendeley-mcp"],
     "env": {
       "MENDELEY_CLIENT_ID": "YOUR_CLIENT_ID",
       "MENDELEY_CLIENT_SECRET": "YOUR_CLIENT_SECRET",
       "MENDELEY_REFRESH_TOKEN": "YOUR_REFRESH_TOKEN"
     }
   }
   ```
4. **`openecon-data`** / **`notebooklm-mcp`** — Optional macro-economic time-series API and NotebookLM cross-document Q&A (requires external MCP installation/auth).
