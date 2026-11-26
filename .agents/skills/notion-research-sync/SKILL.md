---
name: notion-research-sync
description: Integrates the bundled Purple Notion Research Dashboard (Active Researches, Topic, Matrix Literature, Non-Research Documents, AI Disclosure Log) and optional Obsidian Vault notes with Phase 0-7 thesis workflows, especially deep journal dissection (bedah jurnal) and citation tracking.
---

# Notion Research Hub & Obsidian Vault Integration

Use this skill whenever the student chooses to connect **the bundled Purple Notion Research Dashboard** (duplicated into their own Notion workspace) or their **Obsidian Vault** during **Phase 0**, **Phase 1–2 (Journal Dissection / *Bedah Jurnal*)**, **Phase 5–6 (Drafting & Cited Tracking)**, or **Phase 7**.

> **Opt-In Rule:** Notion and Obsidian are strictly **optional**. Never require them if the student chooses *Local Workspace Only*.

---

## 1. Onboarding Setup Flow (Phase 0)

Ask once during Phase 0:
> *"Opsional — apakah ingin menyambungkan catatan riset ke salah satu alat berikut? (1) **Template Notion Research Ungu** (yang sudah diduplikasi ke Notion Anda), (2) **Obsidian Vault** lokal, atau (3) **Folder laptop ini saja**?"*

### If Student Chooses Notion:
1. Check if a Notion MCP server (`notion-local` or Notion official MCP) is already available in the current AI client.
2. **Important Template Structure Note (`Backend Data Vault` vs `Command Hub`):**
   - The duplicated Notion template separates the **Backend Data Vault** (`[Databases] — Researcher`, holding the 5 master source databases) from the **Frontend Command Hub** (which shows linked views + widgets).
   - Always instruct the student to click **`... -> Connections -> Connect to`** at the **Top Root Page** (`Researcher — ...`) so both child pages inherit access cleanly.
   - Always read/write to the **5 master databases inside `[Databases] — Researcher`**, never directly to frontend linked-view blocks—Notion updates all linked views on the Command Hub automatically.
3. **If Notion MCP is active:** Ask the student to paste the URL of their **duplicated Notion Root Page** (or `[Databases] — Researcher`), then discover the 5 master databases inside `[Databases] — Researcher` and store their `database_id` / `data_source_id` in `thesis_config.json` under `integrations.notion`.
4. **If Notion MCP is NOT active (Zero-MCP fallback via `scripts/sync_notion.py`):**
   - Guide the student in 3 plain steps:
     1. Open `https://www.notion.so/my-integrations` -> create an Internal Integration (`AGY Thesis Sync`) and copy the token (`ntn_...` / `secret_...`).
     2. Open the **Top Root Page** of their duplicated Notion template -> click **`...` (top right) -> Connections -> Connect to -> AGY Thesis Sync**.
     3. Paste the token into a local `.env` file as `NOTION_TOKEN=...` (already excluded by `.gitignore`) and share their duplicated Notion page URL, then run:
        ```powershell
        python scripts/sync_notion.py discover --page "<DUPLICATED_ROOT_OR_DB_VAULT_URL>" --config thesis_config.json
        ```

### If Student Chooses Obsidian:
1. Ask for their Obsidian Vault folder path (e.g., `D:\Notes\MyVault`) and save it to `thesis_config.json` -> `integrations.obsidian_vault_path`.
2. Create a dedicated subfolder `<Vault>\Skripsi - <Short Title>\` containing:
   - `00 - Blueprint & Status.md` (with `[[wikilinks]]` to literature notes)
   - `01 - Literature Matrix.md`
   - One note per dissected paper (`[[Author (Year)]] - Short Title.md`) with YAML frontmatter (`year`, `doi`, `grade`, `tier`, `stance`, `read_status`, `tags`) matching the exact schema below.

---

## 2. Exact Purple Notion Research Template Architecture (5 Databases)

Respect every database name, property name, select option, relation, and read-only formula below:

### A. `[DB] — Research List` (*ACTIVE RESEARCHES*)
- **Writable Properties:**
  - `Title` (title): Thesis title
  - `Stage` (select): `1. Ideation` | `2. Lit. Review` | `3. Analysis` | `4. Drafting` | `5. Review/Submitted` | `6. Published`
  - `Target Output` (select): `Thesis / Dissertation` | `Scopus Journal` | `SINTA Journal` | `Policy Brief` | `Working Paper`
  - `Target Date` (date, optional)
  - `Topic` (relation -> `[DB] — Topic`)
- **Read-Only Formulas/Rollups (NEVER overwrite):** `Recent Lit Count`, `Lit Count`, `Doc Count`, `Recent Lit %`, `Research Pulse`, `Progress Visual`, `Read Progress`, `Lit Done`.

### B. `[DB] — Topic` (*By Topics*)
- `Topic` (title): Research subtopic / theme mapped to Research Questions (`RM1..RMk`).
- Relates to `Research List`, `Matrix Literature`, `Non-Research Documents`.

### C. `[DB] — Matrix Literature` (*Core Journal Dissection / Bedah Jurnal Engine*)
Populate this database **during Phase 2** whenever dissecting a peer-reviewed paper (or batch from `01. Literature/` / `search_papers.py`):
- **Bibliographic & Links:**
  - `Title` (title): Full article title
  - `Writer` (rich_text): Authors (e.g., `Gupta, A. S.` or `Nguyễn Minh Hà, Pham Tan Minh, & Quan Minh Quoc Binh`)
  - `Year` (number): 4-digit publication year
  - `Journal / Publisher` (rich_text): Full journal + volume/issue/pages (e.g., `IMF Working Papers, 07(184), 1-39`)
  - `DOI` (rich_text): Bare DOI without `https://doi.org/` (e.g., `10.5089/9781451867480.001`) so Notion's `DOI Link` formula renders automatically
  - `CiteKey` (rich_text): Short citation key (e.g., `gupta2007`, `ha2022`)
  - `Cloud/Zotero Link` (url): `zotero://select/library/items/<KEY>` or Open-Access PDF URL
- **Classification & Status:**
  - `Grade` (select): `SCOPUS` | `SINTA 2` | `SINTA 3` | `SINTA 4` | `SINTA 5` | `WORKING PAPER` | `TECHNICAL DOCS` | `UNGRADED`
  - `Tier` (select): `1 — Foundational` | `2 — Directly Relevant` | `3 — Recent`
  - `Read Status` (select): `To Screen` | `Reading` | `Extracted` | `Cited in Draft`
  - `Evidence Role` (multi_select): `Background/Gap` | `Theory/Framework` | `Methodology` | `Supporting Finding` | `Contradicting Finding`
  - `Section` (multi_select, optional): `Bab I — Pendahuluan` | `Bab II — Tinjauan Pustaka` | `Bab III — Metode` | `Bab IV — Pembahasan` | `Bab V — Simpulan`
  - `Stance` (select): `Positive/Significant` | `Negative` | `Mixed/Conditional` | `Null/Insignificant` | `Conceptual/Review`
- **Deep Journal Dissection Fields (rich_text — trace strictly to the actual PDF/abstract):**
  - `Background` — Problem context & motivation of the paper
  - `Object Scope` — Policy instrument, sector, or subject studied
  - `Place (Period)` — Country/region and observation years (e.g., `ASEAN-8 (2000-2016)`)
  - `Sample` — Sample size, unit of analysis, data sources
  - `Method` — Econometric / qualitative / simulation method
  - `Variable` — Dependent, independent, and control variables
  - `Key Findings` — Exact verified numeric coefficients, signs, significance, or qualitative findings
  - `Conclusion` — Core conclusion of the paper
  - `Discussions` — How it compares to our thesis framework / Indonesian context
  - `Limitations` — Methodological or data weaknesses admitted/observed
  - `Gaps` — Open gaps left unaddressed (especially why our thesis is needed)
  - `Research Contribution` — Specific value this paper adds to our thesis
- **Relations:** `Related Research` (-> active `[DB] — Research List` row), `Topic` (-> `[DB] — Topic` rows), `Builds On` / `Cited By` (optional self-relations).
- **Page Body (`Reading & Appraisal Notes` Callout):**
  Inside every dissected `[DB] — Matrix Literature` page, write a structured callout/note with 3 concise anchors:
  - **Core Thesis:** 1–2 sentences summarizing the paper's central claim.
  - **Key Quotes/Page Ref:** Exact verified numbers, tables, or page/section pointers from the source PDF.
  - **How It Links to My Draft:** Exact chapters/subchapters (`Bab I (1.1)`, `Bab II (2.3 Tabel II.1)`, `Bab IV (4.4)`) where it is used.
- **Read-Only Formulas (NEVER overwrite):** `Is Recent (≤5y)`, `DOI Link`, `Quick Citation`, `Recency`, `Synthesis Snapshot`, `Is Synthesized`.

### D. `[DB] — Non-Research Documents` (*Statutes, Reports, Datasets, Books*)
Use for Indonesian laws/PMKs (`UU`, `PP`, `PMK`, `PER`), BPS/Kemenkeu/IMF/World Bank datasets, and government reports:
- `Title` (title), `Type` (select: `Book` | `Data` | `Report` | `Statute` | `Web Page` | `Working Paper`), `Source` (rich_text), `Year` (number), `Key Parameters` (rich_text), `Status` (status: `Untouched` | `Still processing` | `Archived`), `Cloud / Doc Link` (url), `Related Research` (relation), `Topic` (relation).

### E. `[DB] — AI Disclosure Log` (*TRACC Audit Trail*)
Log major AI-assisted research milestones cleanly for transparency:
- `GenAI Version` (title, e.g., `AGY / Claude / Gemini (Phase 2 - Literature Dissection)`), `Part Using GenAI` (rich_text), `Objectives` (rich_text), `Prompt Used` (rich_text), `Output` (rich_text), `Verification` (rich_text), `Accuracy` (1–5), `Relevance` (1–5), `Completeness` (1–5), `Trustworthiness` (1–5), `Citation Integrity` (1–5), `Related Research` (relation).

---

## 3. Lifecycle Sync Triggers Across Phases 1–7

- **Phase 1B (Title Locked):** Create/update row in `[DB] — Research List` (`Stage = "1. Ideation"`) + create core subtopic rows in `[DB] — Topic`.
- **Phase 2 (Bedah Jurnal):** Set `Stage = "2. Lit. Review"`, push every dissected paper to `[DB] — Matrix Literature` (with `Read Status = "Extracted"` and `Reading & Appraisal Notes` callout), and push regulations/datasets to `[DB] — Non-Research Documents`.
- **Phase 4–5 (Blueprint & Proposal):** Set `Stage = "4. Drafting"` (or `"3. Analysis"` first if quantitative data work begins), run `sync_notion.py mark-cited` so papers cited in `Bab I–III` flip `Read Status -> "Cited in Draft"` (updating Notion's `Progress Visual` bar automatically!).
- **Phase 6 (Analysis & Bab IV–V):** Set `Stage = "3. Analysis"` during data analysis, then `"4. Drafting"`; re-run `mark-cited` after finishing Chapters IV–V and log AI verification in `[DB] — AI Disclosure Log`.
- **Phase 7 (Complete DOCX Ready):** Set `Stage = "5. Review/Submitted"`.
