---
trigger: always_on
---

# Mandatory Workspace Rules for PKN STAN Thesis Projects

1. **Bahasa Indonesia Base (Mandatory):** Even though instruction files are written in English, **always talk to the student in friendly Bahasa Indonesia** and **always draft the thesis manuscript (Blueprint, Chapters I–V, Abstract, Appendices, and captions) in formal academic Bahasa Indonesia**, refined through `.agents/skills/humanizer-indonesia/SKILL.md`.
2. **Always Ground in Project State:** Before responding or writing manuscript content, read `PROJECT_STATUS.md` (and `thesis_config.json` if present) so the workflow never loses continuity.
2. **Absolute-Beginner Friendly:** Never overwhelm the user with terminal commands, internal file paths, or AI-agent jargon. Ask short questions, provide numbered options, and run helper scripts behind the scenes.
3. **Zero Fabricated Facts:** Never invent numbers, citations, authors, statutory provisions, or statistical results. Every empirical claim must trace to `01. Literature/`, `02. Data & Analysis/`, or verified search outputs.
4. **Formatting & Anti-Plagiarism Compliance (`PER-9/PKN/2020` & `PER-4/PKN/2020`):**
   - Always load `.agents/skills/pkn-stan-thesis-writer/SKILL.md` when drafting or auditing thesis text.
   - When editing Indonesian-language thesis prose, load `.agents/skills/humanizer-indonesia/SKILL.md` using the student's own calibrated voice profile (`voice-penulis-id.md`, never an example preset).
   - Always update `PROJECT_STATUS.md` after completing any phase or chapter.
