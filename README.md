# AGY Thesis Starter Kit — STUN Edition

An end-to-end automated research and thesis-writing system powered by **Antigravity (AGY)**, tailored for **STUN** students across all departments and study programs.

Designed specifically for **complete beginners with zero prior knowledge of AI agents or coding**—whether you are **starting from scratch ("from minus")**, **bringing an advisor-approved title**, **uploading an existing Blueprint / Outline**, or **continuing from Proposal Chapters I–III**—all the way through your **Thesis Proposal (Chapters I–III)** and **Complete Thesis (Chapters I–V + References + Appendices + CV)** exported as a submission-ready `.docx` following the **latest official STUN formatting and anti-plagiarism regulations**.

---

## Quick Start in 4 Easy Steps

> Need a step-by-step walkthrough with zero jargon? Read [`docs/BEGINNER_GUIDE.md`](./docs/BEGINNER_GUIDE.md).

1. **Download or Clone This Folder** to your computer (e.g., `D:\My_Thesis\`):
   - Using Git: `git clone https://github.com/adamfadhlurahman/agy-skripsi-stun.git`
   - Or click **Code -> Download ZIP** and extract it.
   - Open the folder in **Antigravity (AGY)**, **Claude Code**, **OpenAI Codex CLI/App**, **Cursor**, or **Gemini CLI**.
   - *(ChatGPT Web users: upload the ZIP and ask ChatGPT to extract it and follow `AGENTS.md`.)*
2. **Install Core Prerequisites (One-Time Setup):**
   - Install **Python 3.10+** (check *"Add Python to PATH"* on Windows).
   - Run `scripts/setup.ps1` (Windows) or `bash scripts/setup.sh` (macOS/Linux)—or ask your AI agent to run it automatically.
   - *(Optional)* Use **Zotero Desktop** (live Word fields) or **Mendeley** (via `.bib` / `.ris` export)—or skip both and rely on built-in `search_papers.py` + automatic APA 7th formatting.
3. **Say Hello in Your Agent Chat:**
   > *"Halo, aku baru mau mulai menyusun skripsi dari nol dan belum punya ide topik sama sekali. Tolong cek kesiapan laptopku dan pandu langkah demi langkah."*
4. **Follow the Guided Workflow (Phase 0 to Phase 7):**
   Just answer your agent's plain-language questions. The agent handles literature mapping, gap testing, voice calibration, manuscript audits, and Word `.docx` generation automatically.

## Universal AI Agent Compatibility

| AI Agent / Harness | Entry File Loaded Automatically | Compatibility Notes |
|---|---|---|
| **Antigravity (AGY)** | `AGENTS.md`, `GEMINI.md`, `.agents/rules/thesis-guard.md` | Full native automation (recommended). |
| **Claude Code** | `CLAUDE.md` -> `@AGENTS.md` + `.agents/skills/` | Full workflow & local scripts supported. |
| **OpenAI Codex CLI / App** | `AGENTS.md` + `.agents/skills/` | Full native discovery & terminal automation. |
| **Cursor** | `AGENTS.md` + `.cursor/rules/thesis-guard.mdc` | Full native rule & skill workflow. |
| **Gemini CLI** | `GEMINI.md` + `AGENTS.md` + `.agents/skills/` | Full native workspace discovery. |
| **ChatGPT Web (Code Sandbox)** | Upload ZIP + prompt *"Follow `AGENTS.md`"* | Builds full `.docx` on Linux sandbox; refresh TOC manually (`Ctrl+A -> F9`) in Word afterward. |

---

## Complete Workflow (Start From Any Stage -> Defense-Ready)

Your AI agent detects what you already have (or asks in the first chat) and **automatically skips completed stages**, picking up cleanly from whichever milestone is untouched:

| Phase | What Happens | Can Start Directly Here? |
|---|---|---|
| **Phase 0** | Automatic Python/Zotero readiness check, existing-file scan, & student/program profile (`thesis_config.json`). | Always runs in 1 minute |
| **Phase 1A ("From Minus")** | If you have no idea yet, your agent explores your favorite courses, past project experience, and open datasets -> 3–5 topic options. | Yes (no idea yet) |
| **Phase 1B (Gap Testing)** | Tests your top 1–2 candidate titles across 3 gates (open gap, contribution, feasibility) and locks 1 Title + Thesis Archetype. | Yes (rough idea) |
| **Phase 2 (Literature & Citations)** | Finds peer-reviewed papers via built-in OpenAlex/CrossRef search (`search_papers.py`), builds a Literature Matrix, and syncs **Zotero or Mendeley**. | Yes (approved title) |
| **Phase 3 (Voice Calibration)** | Analyzes 1–2 of your own past writing samples (`05. Voice Reference/` or your existing chapters) so prose sounds like you. | Auto-runs before drafting |
| **Phase 4 (Research Blueprint)** | Locks Research Questions, Operational Definitions, Data Map, and Subchapter Outline in `03. Drafts/Thesis Blueprint.md`. | Yes (existing outline/notes) |
| **Phase 5 (Proposal Chapters I–III)** | Imports/aligns your existing Blueprint (if provided), drafts Chapters I–III, runs formatting/anti-AI/n-gram audits, and exports `Proposal_Thesis.docx`. | Yes (existing Blueprint) |
| **Phase 6 (Analysis & Chapters IV–V)** | Imports/audits your existing Chapters I–III (if provided), analyzes data in `02. Data & Analysis/`, generates 300 DPI figures, and drafts Chapters IV–V + Abstract (<= 250 words). | Yes (existing Proposal / post-Sempro) |
| **Phase 7 (Final Thesis `.docx`)** | Polishes language/citations and compiles the complete document (`Cover` through `CV`) into `04. Output DOCX/Complete_Thesis.docx`. | Yes (existing Chapters I–V) |

---

## Workspace Folder Structure

* `01. Literature/` — Store all PDF journal articles, books, and regulations here.
* `02. Data & Analysis/` — Raw datasets, Excel/CSV files, analysis scripts, and 300 DPI figures.
* `03. Drafts/` — `Thesis Blueprint.md`, `Chapter I`–`Chapter V`, `Abstract.md`, and `Appendices`.
* `04. Output DOCX/` — Built `Proposal_Thesis.docx` and `Complete_Thesis.docx` files.
* `05. Voice Reference/` — Place 1–2 of your own earlier essays/papers here for style calibration.
* `.agents/skills/` — **16 local AGY skills pre-bundled** out of the box (no manual plugin installation required).
* `scripts/` — Ready-to-run Python utilities (`search_papers.py` for OpenAlex/CrossRef + OA PDFs, `build_zotero_map.py` for hybrid Zotero & Mendeley `.bib`/`.ris`/SQLite, `sync_notion.py` for optional Notion Research Dashboard sync, voice extractor, manuscript auditor, `.docx` builder, and verifier).
* `templates/` — Clean blank Word template conforming to the latest STUN formatting standards.

## Optional Knowledge Hub Integrations

* **Bundled Notion Research Dashboard:** Connect your duplicated purple Notion Research Template (`scripts/sync_notion.py` or Notion MCP) so deep journal dissections (`Matrix Literature`), statutes/datasets (`Non-Research Documents`), TRACC AI logs, and `Cited in Draft` progress bars sync automatically during Phase 2–7.
* **Obsidian Vault:** Optionally mirror `[[wikilink]]` literature notes and your Blueprint directly into your local Obsidian vault.

---

## License & Third-Party Attributions

* **Original Starter Kit Components:** See [`LICENSE`](./LICENSE).
* **Open-Source Skills & Attributions:** This starter kit integrates permissive open-source agent skills licensed under **MIT** and **CC0 1.0 Universal** (`humanizer-indonesia` by Pribadi Mumpuni Adhi, `ai-research-skills` by Wenyu Chiou, and `EconAgentSkills` by Jonas Weinert). Full copyright notices, upstream repository links, and license texts are provided in [`THIRD_PARTY_NOTICES.md`](./THIRD_PARTY_NOTICES.md).
