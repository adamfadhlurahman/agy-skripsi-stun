---
name: thesis-autopilot
description: Orchestrates end-to-end PKN STAN Thesis Proposal (Chapters I-III) and Complete Thesis (Chapters I-V) production from zero/minus (no topic idea yet) to a submission-ready DOCX strictly conforming to PER-9/PKN/2020 and PER-4/PKN/2020. Always activate at session start or whenever the user asks for the next step.
---

# PKN STAN Thesis End-to-End Autopilot (Phase 0 – Phase 7)

This skill guides PKN STAN students—including complete beginners with zero AI or coding experience—through the full thesis lifecycle without exposing technical commands or jargon. Run phases sequentially, keep `PROJECT_STATUS.md` updated after every milestone, and request explicit student approval at each decision gate.

> **Language & Communication Rule:** Always speak to the student in **friendly, jargon-free Bahasa Indonesia** and draft all thesis deliverables in **formal academic Bahasa Indonesia** (with `humanizer-indonesia` applied), even though this runbook is written in English. Present 2–4 concrete numbered options whenever user input is needed.

---

## Phase 0 — Onboarding & Readiness Check

1. **Silent Environment Check:**
   - Run `python scripts/setup_check.py`.
   - If required Python packages are missing and the user agrees, run `powershell -ExecutionPolicy Bypass -File scripts/setup.ps1` (or `pip install -r requirements.txt`).
   - Report readiness simply (e.g., *"Word builder & language checker are ready; Zotero isn't open yet—we'll enable it in Phase 2"*).
2. **Short Onboarding Interview (3–4 Simple Questions):**
   - Full Name & NPM (Student ID).
   - Department, Study Program, and Concentration at **PKN STAN** (`D-IV Akuntansi Sektor Publik`, `D-IV Manajemen Keuangan Negara`, `D-IV Manajemen Aset Publik`, or another program).
   - Academic Advisor & Program Chair names (if assigned; otherwise keep clean placeholders).
   - **Starting Point (Never force users who already have progress to restart from zero):**
     1. *Completely blank ("from minus")* -> Full **Phase 1A–7**.
     2. *Have a rough topic/interest or PKL/KTTA idea* -> Brief **Phase 1A**, then **Phase 1B–7**.
     3. *Already have an advisor-approved title* -> Populate `thesis_config.json`, pick the `PER-9/PKN/2020` archetype, and jump to **Phase 2–7**.
     4. *Already have a Thesis Blueprint / Outline (or partial literature/notes)* -> Run the **Adaptive Existing-Work Intake** below, sync `Blueprint Skripsi.md` & `thesis_config.json`, verify `Phase 2` literature & `Phase 3` voice calibration, mark completed phases `[x]` in `PROJECT_STATUS.md`, and jump to **Phase 5–7**.
     5. *Already have Proposal (`Bab I–III`, `.docx`/`.md`) / Post-Sempro* -> Run **Adaptive Existing-Work Intake**, import/audit Chapters I–III, mark Phases 0–5 `[x]` (completing any missing `zotero_map.json` / `voice-penulis-id.md` gaps), and execute **Phase 6–7** through final submission `.docx`.
     6. *Already have a full draft (`Bab I–V`)* -> Run **Adaptive Existing-Work Intake**, run `audit_manuscript.py` + `humanizer-indonesia` + citation matching (`zotero_map.json`), and build the submission-ready `.docx` in **Phase 7**.
3. **Phase 0 Output:**
   - Copy `thesis_config.example.json` to `thesis_config.json` and fill in student identity, program, and chapter labels.
   - Update `PROJECT_STATUS.md` (check off Phase 0 and any earlier stages skipped/imported).

---

## Adaptive Existing-Work Intake (When the Student Already Has a Blueprint, Proposal, or Draft)

Whenever a student arrives with existing work (a blueprint, outline, literature folder, dataset, Proposal `Bab I–III`, or full draft `Bab I–V`), **never ask them to re-invent their topic or redo finished stages**. Follow this 4-step intake:

1. **Inspect & Extract Without Overwriting:**
   - Read whatever files the student provides or places in `01. Literature/`, `02. Data & Analysis/`, or `03. Drafts/` (if `.docx` or `.pdf`, extract text with `python-docx` / `pymupdf` / `scripts/extract_voice_sample.py`).
   - Preserve the student's approved title, research questions (`RM1..RMk`), variables/criteria, methodology, and substantive arguments. Only propose adjustments if there is a factual contradiction or a `PER-9/PKN/2020` / `PER-4/PKN/2020` compliance issue.
2. **Map to Workspace Contract:**
   - **If starting from a Blueprint / Outline:** Convert or align it into `03. Drafts/Blueprint Skripsi.md` (confirming `PER-9/PKN/2020` archetype, research questions, operational definitions, data sources, and subchapter structure `1.1..5.x`), populate `thesis_config.json`, and check whether `01. Literature/` + `zotero_map.json` need to be populated before Phase 5.
   - **If starting from Proposal (`Bab I–III`) or Full Draft (`Bab I–V`):** Reconstruct `Blueprint Skripsi.md` from their existing chapters (so Chapters IV–V stay 100% consistent), split/convert chapters into clean Markdown (`03. Drafts/Bab I ...md` etc.), and extract their citations into `zotero_map.json`.
   - **Smart Voice Calibration Shortcut:** If the student did not supply a separate essay in `05. Voice Reference/`, extract prose from their own existing `Bab I–III` / proposal text using `scripts/extract_voice_sample.py` to build `voice-penulis-id.md`!
3. **Confirm Fast Gap-Fill Plan with the Student:**
   - Present a short checklist showing: **(a) Phases already covered by their files** (marked `[x]`), **(b) Any small missing prerequisites** (e.g., Zotero map, voice calibration, or dataset check), and **(c) Exact next phase AGY will execute through Phase 7**. Ask for confirmation before editing or drafting.
4. **Execute Through Completion (Phase 7):**
   - Run all remaining phases seamlessly—always finishing with `audit_manuscript.py`, `humanizer-indonesia`, `generate_citation_specs.py`, `build_thesis_docx.py`, `update_word_fields.py`, and `verify_thesis_docx.py` so the final `.docx` is genuinely complete and verified.

---

## Phase 1A — "From Minus" Topic Discovery (When You Have No Idea Yet)

Read [`references/program_and_data_catalog.md`](./references/program_and_data_catalog.md) and internally activate **`research-ideation`**.

1. **Diagnose 4 Comfort Anchors (in plain, friendly language):**
   - *Academic Anchor:* 2–3 favorite courses, past Diploma III KTTA topic, or internship (PKL) unit.
   - *Preferred Work Style:*
     - Working with numbers, financial statements, or regressions (`Quantitative`)
     - Interviews, policy implementation, or case studies (`Qualitative`)
     - Policy/rate/incentive scenario modeling (`Descriptive Simulation`)
     - Designing an information system, dashboard, or control workflow (`Descriptive Design`)
   - *Realistic Data Access:* Access to an organizational/PKL office dataset (KPP, KPPN, Customs/Bea Cukai, KPKNL, Pemda, BPK, BLU), OR prefer **open public datasets** (Kemenkeu/APBN, DJPK, BPS, IDX/BEI, OJK, BI, BPK IHPS/LHP, JDIH)?
   - *Tool Comfort:* Excel only, Python/R/Stata, or full AGY assistance?
2. **Propose & Screen Options (Traffic-Light Feasibility):**
   - Present **3–5 concrete title options**, each stating: **(a) Policy/Object, (b) Analytical Lens/Variables, (c) `PER-9` Archetype, (d) Real Data Source, (e) Feasibility Rating (Green / Yellow / Red)**.
   - Steer beginners away from *RED* options (restricted/confidential taxpayer microdata without written clearance).

---

## Phase 1B — Title Sharpening & Gap Verification (*Gate 1*)

Internally activate **`gap-to-topic`** for the student's **top 1–2 candidates**:

1. Run real literature searches (`paper-search` MCP if active; otherwise **built-in zero-MCP `python scripts/search_papers.py --query "<topic>" --limit 10`** for OpenAlex/CrossRef peer-reviewed DOIs, abstracts, and citation counts, plus `search_web` for Indonesian regulations/JDIH/BPS). **Never** execute `research-hub` CLI commands or Node.js `.js` scripts (`dossier_to_docx.js` / `brief_to_docx.js`)—save all dossiers cleanly as Markdown in `.research/topic_dossier.md` and note search coverage limits transparently.
2. Evaluate **3 Decision Gates**:
   - **Gate 1 (Open?):** Has this exact angle already been published in recent Indonesian/international journals?
   - **Gate 2 (Contribution?):** What clear value does it add (new period, PMK/policy instrument, metric, or locus)?
   - **Gate 3 (Feasible?):** Can all required data actually be obtained before the proposal/defense deadline?
3. **Gate 1 (Student Decision):**
   - Student locks **1 Main Title** + **`PER-9/PKN/2020` Thesis Archetype** (`quantitative` / `qualitative` / `descriptive_simulation` / `descriptive_design`).
   - Save title, archetype, and Chapters III–IV labels to `thesis_config.json` and `PROJECT_STATUS.md`.

---

## Phase 2 — Literature Collection, Zotero & Synthesis Matrix

Activate **`lit-review-assistant`**, **`literature-triage-matrix`**, and **`paper-summarize`**.

1. Gather recent peer-reviewed journals (5–10 years), official regulations (`JDIH Kemenkeu` / `peraturan.bpk.go.id`), and institutional reports into `01. Literature/` named cleanly (e.g., `Author (Year) - Short Title.pdf`).
   - When `paper-search` MCP is unavailable, run `python scripts/search_papers.py --query "<keywords>" --from-year 2016 --download-oa --export-zotero "03. Drafts/zotero_map.json"` (or `--doi "<doi>"`) to discover verified OpenAlex/CrossRef papers, automatically download legal Open Access PDFs into `01. Literature/`, and populate `03. Drafts/zotero_map.json`.
2. **Hybrid Citation Manager Choice (Zotero OR Mendeley):**
   - Ask whether the student uses **Zotero Desktop** or **Mendeley** (or none yet):
     - **If Zotero:** Guide them to turn on Zotero Desktop & Local API, create a thesis collection (e.g., `Skripsi`), add all references, and run:
       ```powershell
       python scripts/build_zotero_map.py --list-collections
       python scripts/build_zotero_map.py --collection-name "Skripsi" --out "03. Drafts/zotero_map.json"
       ```
     - **If Mendeley (Reference Manager / Desktop):** Export any papers found via `search_papers.py --export-ris "01. Literature/references_mendeley.ris"` for 1-click import into Mendeley, OR read an unencrypted local Mendeley Desktop SQLite / existing `.bib` / `.ris` export into `zotero_map.json`:
       ```powershell
       python scripts/build_zotero_map.py --mendeley-local --collection-name "Skripsi" --out "03. Drafts/zotero_map.json"
       # or from exported BibTeX / RIS:
       python scripts/build_zotero_map.py --bib "01. Literature/library.bib" --provider mendeley --out "03. Drafts/zotero_map.json"
       ```
       *(Supports `--ris` too; and if `mendeley-mcp` is configured by the user, it can be queried directly via MCP. `build_thesis_docx.py` adapts automatically to `provider: "mendeley"` with clean APA 7th in-text citations and `DAFTAR PUSTAKA`).*
     - **If neither manager is installed:** `scripts/search_papers.py --export-zotero "03. Drafts/zotero_map.json"` populates verified CSL-JSON metadata directly, and `build_thesis_docx.py` formats a complete APA 7th bibliography automatically.
3. Build **`.research/literature_matrix.md`** via `literature-triage-matrix` comparing author, year, method, data/sample, core findings, and limitations.
4. *(Optional)* If `notebooklm-mcp` is active, upload key PDFs for cross-document fact verification.

---

## Phase 3 — Author Voice Calibration

**Never skip this phase.** This ensures the manuscript sounds authentically like the student rather than generic AI prose.

1. Ask the student to place **1–2 of their own past writing samples** (such as their Diploma III KTTA or course essays written by themselves) into `05. Voice Reference/`. *(If unavailable, co-draft 3–4 short opinion paragraphs written in the student's own words as a baseline).*
2. Extract clean prose:
   ```powershell
   python scripts/extract_voice_sample.py "05. Voice Reference/<filename>" --out "05. Voice Reference/sample_prose.md"
   ```
3. Profile sentence rhythm:
   ```powershell
   python .agents/skills/humanizer-indonesia/scripts/metrik.py "05. Voice Reference/sample_prose.md" --preset akademik
   ```
4. Copy `.agents/skills/humanizer-indonesia/references/voice-template-id.md` to `.agents/skills/humanizer-indonesia/references/voice-penulis-id.md` and populate the student's actual cadence and phrasing habits. **Never** use someone else's sample profile (`voice-prib-id.md`) for the student's thesis.

---

## Phase 4 — Study Design & Thesis Blueprint (*Gate 2*)

Activate **`research-design-helper`** (walk through the 5 short Socratic segments in plain, accessible language) to produce `.research/design_brief.md`.

Then lock **`03. Drafts/Blueprint Skripsi.md`** (written in Bahasa Indonesia) as the single cross-chapter contract:
1. Research Questions (`RM1..RMk`) aligned 1-to-1 with Objectives and Conclusions.
2. Operational Definitions / Evaluation Criteria / System Specifications (matching the chosen `PER-9/PKN/2020` Art. 3.1.2.1 archetype).
3. Primary & Secondary Data Map + file locations in `02. Data & Analysis/` + contingency plan (`PER-9` Art. 2.4).
4. Analytical Method / Empirical Model / Testing Protocol / Architecture Spec.
5. Full Subchapter Outline (`1.1` through `5.x`) conforming to `PER-9/PKN/2020`.

**Gate 2:** Obtain explicit student sign-off on `Blueprint Skripsi.md` before drafting full chapters.

---

## Phase 5 — Proposal Drafting, Multi-Layer Audit & Export (Chapters I–III)

1. Load `.agents/skills/pkn-stan-thesis-writer/SKILL.md` and `03. Drafts/Blueprint Skripsi.md`.
2. Draft incrementally in formal academic Bahasa Indonesia into `03. Drafts/`:
   - `Bab I - Pendahuluan.md`
   - `Bab II - Landasan Teori.md`
   - `Bab III - Metode Penelitian.md` (or `Inti Penelitian` / `Analisis Sistem yang Berjalan` depending on `PER-9` archetype).
   - Proposal schedule appendix (e.g., `03. Drafts/Lampiran 1 - Jadwal Kegiatan.md`) if needed.
3. **Audit After Every Chapter:**
   - Run `python scripts/audit_manuscript.py "03. Drafts/<Chapter>.md" --against "05. Voice Reference/sample_prose.md"` (plus key PDFs in `01. Literature/` for `PER-4/PKN/2020` n-gram overlap checks).
   - Run `metrik.py` and polish Indonesian prose with `.agents/skills/humanizer-indonesia/SKILL.md` using `voice-penulis-id.md`.
   - Run **`paper-review`** (developmental mode) to catch logic gaps before advisor review.
4. Auto-match citations into `03. Drafts/citation_specs.json`, then build and verify Proposal `.docx`:
   ```powershell
   python scripts/generate_citation_specs.py --config thesis_config.json
   python scripts/build_thesis_docx.py --config thesis_config.json --mode proposal
   python scripts/verify_thesis_docx.py --config thesis_config.json --mode proposal
   ```

---

## Phase 6 — Data Analysis, Chapters IV–V & Cross-Chapter Sync

1. Analyze data in `02. Data & Analysis/` with the best-fit tool:
   - Python/panel: `working-with-data`, `python-panel-data`
   - R/Stata: `r-econometrics`, `stata-data-cleaning`, `stata-regression`
   - Publication-grade 300 DPI figures: `econ-visualization` (save PNGs to `02. Data & Analysis/figures/` and register in `thesis_config.json` -> `paths.figures`).
2. Persist verified summary tables/outputs (e.g., Excel master workbook or `results_summary.json`) before writing Chapter IV.
3. Draft `Bab IV` & `Bab V` (in formal academic Bahasa Indonesia), `03. Drafts/Abstrak.md` (<= 250 words per `PER-9` Art. 3.1.1.2), `03. Drafts/Lampiran*.md`, and update `03. Drafts/citation_specs.json` via `python scripts/generate_citation_specs.py --config thesis_config.json`.
4. **Mandatory Post-Research Sync:** Update `Chapters I–III` from planned/future phrasing to executed phrasing where required, and verify 100% consistency of sample sizes, periods, and research questions across Chapters I–V. Also remind the student to fill in `riwayat_hidup` in `thesis_config.json` before final compilation.
5. Run `audit_manuscript.py`, `metrik.py`, `humanizer-indonesia`, and `paper-review` (submission mode) across all chapters.

---

## Phase 7 — Final Thesis Compilation & Defense Checklist

1. Build the complete thesis (`Cover`, `Approval Page`, `Examination Pass Statement`, `Originality Statement`, `Preface`, `TOC/Tables/Figures/Appendices`, `Abstract`, `Chapters I–V`, `References`, `Appendices`, `CV`):
   ```powershell
   python scripts/build_thesis_docx.py --config thesis_config.json --mode thesis
   ```
2. If Microsoft Word is installed on Windows, refresh all Word fields automatically and verify:
   ```powershell
   python scripts/update_word_fields.py "04. Output DOCX/Complete_Thesis.docx"
   python scripts/verify_thesis_docx.py --config thesis_config.json --mode thesis
   ```
3. Guide the student through the final Word checklist in simple terms:
   - Open `04. Output DOCX/Complete_Thesis.docx` in Microsoft Word.
   - Click the **Zotero** tab -> **Refresh** to activate all live citations and the Reference List.
   - Press `Ctrl+A` then `F9` (*Update entire table*) if page numbers need one final refresh after Zotero updates.
   - Visually inspect chapter start pages (7.5 cm top margin, bottom-center page number), approval/statement pages, tables, and figures, and walk through [`docs/DEFENSE_CHECKLIST.md`](./../../docs/DEFENSE_CHECKLIST.md) before submitting to the academic portal and Turnitin (`PER-4/PKN/2020`).
