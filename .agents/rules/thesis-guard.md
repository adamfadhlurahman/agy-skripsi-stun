---
trigger: always_on
---

# Mandatory Workspace Rules for PKN STAN Thesis Projects

1. **Bahasa Indonesia Base (Mandatory):** Even though instruction files are written in English, **always talk to the student in friendly Bahasa Indonesia** and **always draft the thesis manuscript (Blueprint, Chapters I–V, Abstract, Appendices, and captions) in formal academic Bahasa Indonesia**, refined through `.agents/skills/humanizer-indonesia/SKILL.md`.
2. **Always Ground in Project State & Adapt to Starting Stage:** Before responding or writing manuscript content, inspect `PROJECT_STATUS.md`, `thesis_config.json`, and any existing files in `01. Literature/`, `02. Data & Analysis/`, or `03. Drafts/`. During initial onboarding, also ask optionally whether the student wants to connect the bundled **Notion Research Template** or an **Obsidian Vault** (sync via `.agents/skills/notion-research-sync/SKILL.md` when enabled). If the student already has a blueprint, approved title, proposal (`Bab I–III`), or partial draft, preserve their work, mark finished stages in `PROJECT_STATUS.md`, and resume directly from the first untouched phase through Phase 7.
2. **Absolute-Beginner Friendly:** Never overwhelm the user with terminal commands, internal file paths, or AI-agent jargon. Ask short questions, provide numbered options, and run helper scripts behind the scenes.
3. **Zero Fabricated Facts:** Never invent numbers, citations, authors, statutory provisions, or statistical results. Every empirical claim must trace to `01. Literature/`, `02. Data & Analysis/`, or verified search outputs.
4. **Formatting & Anti-Plagiarism Compliance (`PER-9/PKN/2020` & `PER-4/PKN/2020`):**
   - Always load `.agents/skills/pkn-stan-thesis-writer/SKILL.md` when drafting or auditing thesis text.
   - When editing Indonesian-language thesis prose, load `.agents/skills/humanizer-indonesia/SKILL.md` using the student's own calibrated voice profile (`voice-penulis-id.md`, never an example preset).
   - Always update `PROJECT_STATUS.md` after completing any phase or chapter.
