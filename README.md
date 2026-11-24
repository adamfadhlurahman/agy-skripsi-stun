# AGY Thesis Starter Kit — STUN Edition

An end-to-end automated research and thesis-writing system powered by **Antigravity (AGY)**, tailored for **STUN** students across all departments and study programs.

Designed specifically for **complete beginners with zero prior knowledge of AI agents or coding**—even if you are **starting from scratch with no topic idea yet**—all the way through your **Thesis Proposal (Chapters I–III)** and **Complete Thesis (Chapters I–V + References + Appendices + CV)** exported as a submission-ready `.docx` following the **latest official STUN formatting and anti-plagiarism regulations**.

---

## Quick Start in 4 Easy Steps

> Need a step-by-step walkthrough with zero jargon? Read [`docs/BEGINNER_GUIDE.md`](./docs/BEGINNER_GUIDE.md).

1. **Download or Clone This Folder** to your computer (e.g., `D:\My_Thesis\`):
   - Using Git: `git clone https://github.com/adamfadhlurahman/agy-skripsi-stun.git`
   - Or click **Code -> Download ZIP** and extract it.
   - Open the folder in **Antigravity (AGY)** (`File -> Open Folder...`).
2. **Install Core Prerequisites (One-Time Setup):**
   - Install **Python 3.10+** (check *"Add Python to PATH"* on Windows).
   - *(Recommended)* Install **Zotero Desktop** so citations and your Reference List update live inside Microsoft Word.
   - You don't need to run complicated commands yourself—AGY can check and set things up for you in your first chat.
3. **Say Hello in the AGY Chat:**
   > *"Halo, aku baru mau mulai menyusun skripsi dari nol dan belum punya ide topik sama sekali. Tolong cek kesiapan laptopku dan pandu langkah demi langkah."*
4. **Follow the Guided Workflow (Phase 0 to Phase 7):**
   Just answer AGY's plain-language questions. AGY handles literature mapping, gap testing, voice calibration, manuscript audits, and Word `.docx` generation automatically.

---

## Complete Workflow (From Minus to Defense-Ready)

| Phase | What Happens |
|---|---|
| **Phase 0** | Automatic Python/Zotero readiness check & student/program profile setup (`thesis_config.json`). |
| **Phase 1A ("From Minus")** | If you have no idea yet, AGY explores your favorite courses, past project experience, data comfort level, and matches them against accessible open datasets. |
| **Phase 1B (Gap Testing)** | Tests your top 1–2 candidate titles across 3 gates (open gap, clear contribution, data feasibility) and locks 1 Title + Thesis Archetype (*Quantitative / Qualitative / Descriptive Simulation / Descriptive Design*). |
| **Phase 2 (Literature & Zotero)** | Collects peer-reviewed papers and official regulations into `01. Literature/`, builds a Literature Triage Matrix, and links Zotero. |
| **Phase 3 (Voice Calibration)** | Analyzes 1–2 of your own past writing samples (`05. Voice Reference/`) so your thesis sounds genuinely like you, not generic AI prose. |
| **Phase 4 (Research Blueprint)** | Locks Research Questions, Operational Definitions, Data Map, and Subchapter Outline in `03. Drafts/Thesis Blueprint.md`. |
| **Phase 5 (Proposal Chapters I–III)** | Drafts Chapters I–III, runs formatting/anti-AI/n-gram overlap audits, performs peer-reviewer critique, and exports `04. Output DOCX/Proposal_Thesis.docx`. |
| **Phase 6 (Analysis & Chapters IV–V)** | Analyzes data in `02. Data & Analysis/`, generates 300 DPI charts, drafts Chapters IV–V + Abstract (<= 250 words), and syncs Chapters I–III. |
| **Phase 7 (Final Thesis `.docx`)** | Compiles the complete document (`Cover`, `Approval`, `Examination Pass`, `Originality Statement`, `Preface`, `TOC/Tables/Figures/Appendices`, `Abstract`, `Chapters I–V`, `References`, `Appendices`, `CV`) into `04. Output DOCX/Complete_Thesis.docx`. |

---

## Workspace Folder Structure

* `01. Literature/` — Store all PDF journal articles, books, and regulations here.
* `02. Data & Analysis/` — Raw datasets, Excel/CSV files, analysis scripts, and 300 DPI figures.
* `03. Drafts/` — `Thesis Blueprint.md`, `Chapter I`–`Chapter V`, `Abstract.md`, and `Appendices`.
* `04. Output DOCX/` — Built `Proposal_Thesis.docx` and `Complete_Thesis.docx` files.
* `05. Voice Reference/` — Place 1–2 of your own earlier essays/papers here for style calibration.
* `.agents/skills/` — **16 local AGY skills pre-bundled** out of the box (no manual plugin installation required).
* `scripts/` — Ready-to-run Python utilities (setup checker, voice extractor, manuscript auditor, Zotero sync, `.docx` builder, and verifier).
* `templates/` — Clean blank Word template conforming to the latest STUN formatting standards.

---

## License & Third-Party Attributions

* **Original Starter Kit Components:** See [`LICENSE`](./LICENSE).
* **Open-Source Skills & Attributions:** This starter kit integrates permissive open-source agent skills licensed under **MIT** and **CC0 1.0 Universal** (`humanizer-indonesia` by Pribadi Mumpuni Adhi, `ai-research-skills` by Wenyu Chiou, and `EconAgentSkills` by Jonas Weinert). Full copyright notices, upstream repository links, and license texts are provided in [`THIRD_PARTY_NOTICES.md`](./THIRD_PARTY_NOTICES.md).
