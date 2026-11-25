# Claude Code Instructions — AGY Thesis Autopilot

@AGENTS.md

## Claude Code Path & Skill Discovery Bridge

Claude Code reads this file automatically at startup. Follow every rule in [`AGENTS.md`](./AGENTS.md) and always inspect [`PROJECT_STATUS.md`](./PROJECT_STATUS.md), [`thesis_config.json`](./thesis_config.json) (if present), and any user-provided files in `01. Literature/`, `02. Data & Analysis/`, or `03. Drafts/` before responding. Always offer adaptive entry points (starting from minus, rough idea, approved title, existing blueprint, existing Proposal Chapters I–III, or existing full draft) so buyers continue smoothly from their current stage through Phase 7.

Because bundled skills live in `.agents/skills/` (shared across Antigravity, Codex CLI, Gemini CLI, Cursor, and Claude Code), **read the relevant `SKILL.md` files from `.agents/skills/<name>/SKILL.md`** directly using your file-reading tool according to the active phase:

- **End-to-End Orchestrator (Phases 0–7):** `.agents/skills/thesis-autopilot/SKILL.md`
- **PKN STAN Formatting & Anti-Plagiarism Rules (`PER-9/PKN/2020`, `PER-4/PKN/2020`):** `.agents/skills/pkn-stan-thesis-writer/SKILL.md`
- **Indonesian Prose & Voice Calibration:** `.agents/skills/humanizer-indonesia/SKILL.md` (metrics check: `python .agents/skills/humanizer-indonesia/scripts/metrik.py <file> --preset akademik`)
- **Ideation & Gap Testing (Phase 1):** `.agents/skills/research-ideation/SKILL.md`, `.agents/skills/gap-to-topic/SKILL.md`
- **Literature & Peer Review (Phases 2, 5, 6):** `.agents/skills/lit-review-assistant/SKILL.md`, `.agents/skills/literature-triage-matrix/SKILL.md`, `.agents/skills/paper-summarize/SKILL.md`, `.agents/skills/paper-review/SKILL.md`, `.agents/skills/research-hub/SKILL.md`
- **Study Design (Phase 4):** `.agents/skills/research-design-helper/SKILL.md`
- **Data Analysis & Figures (Phase 6):** `.agents/skills/working-with-data/SKILL.md`, `.agents/skills/python-panel-data/SKILL.md`, `.agents/skills/r-econometrics/SKILL.md`, `.agents/skills/stata-data-cleaning/SKILL.md`, `.agents/skills/stata-regression/SKILL.md`, `.agents/skills/econ-visualization/SKILL.md`

## Cross-OS Notes
- On **Windows**, use `scripts/setup.ps1` and `python scripts/update_word_fields.py`.
- On **macOS / Linux**, use `bash scripts/setup.sh`. Because Microsoft Word COM is Windows-only, `update_word_fields.py` safely exits with a reminder for the student to update fields manually inside Word (`Select All -> Update Field` / `F9`).
