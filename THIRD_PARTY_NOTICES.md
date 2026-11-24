# Third-Party Notices & Attributions

The **AGY Thesis Starter Kit (STUN Edition)** combines original STUN thesis automation workflows with permissive open-source agent skills licensed under **MIT** and **CC0 1.0 Universal**. This notice provides complete attribution and license compliance for all upstream authors.

---

## 1. Original Starter Kit Components

The following files are original works designed for end-to-end STUN proposal and thesis drafting in accordance with the latest official university formatting and anti-plagiarism regulations:

* `AGENTS.md`, `GEMINI.md`, `README.md`, `PROJECT_STATUS.md`, `.gitignore`, `LICENSE`
* `.agents/skills/thesis-autopilot/`
* `.agents/skills/stun-thesis-writer/`
* `.agents/rules/` & `docs/`
* `scripts/` (`build_thesis_docx.py`, `verify_thesis_docx.py`, `audit_manuscript.py`, `build_zotero_map.py`, `extract_voice_sample.py`, `update_word_fields.py`, `setup_check.py`, `setup.ps1`)
* `templates/Template_STUN_Blank.docx`, `thesis_config.example.json`, `03. Drafts/citation_specs.example.json`

---

## 2. Third-Party Open-Source Skills

### A. Humanizer Indonesia (`humanizer-indonesia`)
* **Author / Copyright Holder:** Pribadi Mumpuni Adhi (`@adhiprib`)
* **Upstream Repository:** <https://github.com/adhiprib/humanizer-indonesia>
* **License:** **MIT License** — Copyright (c) 2026 Pribadi Mumpuni Adhi
* **Location in This Repo:** `.agents/skills/humanizer-indonesia/` (original `LICENSE` file preserved inside)
* **Role:** Indonesian academic prose refinement, AI-tell detection (`id-ai-tells.md`), author-voice calibration template (`voice-template-id.md`), and sentence-rhythm profiler (`scripts/metrik.py`).

### B. AI Research Skills (`ai-research-skills`)
* **Author / Copyright Holder:** Wenyu Chiou (`@WenyuChiou`)
* **Upstream Repository:** <https://github.com/WenyuChiou/ai-research-skills>
* **License:** **MIT License** — Copyright (c) 2026 Wenyu Chiou
* **Location in This Repo:**
  * `.agents/skills/gap-to-topic/` (3-gate research gap & feasibility dossier)
  * `.agents/skills/research-design-helper/` (5 Socratic study-design segments)
  * `.agents/skills/literature-triage-matrix/` (Cross-paper synthesis matrix)
  * `.agents/skills/paper-review/` (Reviewer-style manuscript critique)
  * `.agents/skills/paper-summarize/` (Evidence-located paper summaries)
  * `.agents/skills/research-hub/references/` (`research-protocol.md` and `source-claim-audit.md` evidence contracts)
* **Compliance Note:** Original MIT `LICENSE` files are preserved inside every directory above without altering license terms.

### C. EconAgentSkills (`EconAgentSkills`)
* **Author / Copyright Holder:** Jonas Weinert (`@JonasWeinert`) and contributors (inspired by `meleantonio/awesome-econ-ai-stuff` and World Bank DIME Analytics standards)
* **Upstream Repository:** <https://github.com/JonasWeinert/EconAgentSkills>
* **License:** **CC0 1.0 Universal (Public Domain Dedication)** — permits free copying, modification, and distribution, including for commercial purposes
* **Location in This Repo:**
  * `.agents/AGENT_POLICY.md`
  * `.agents/skills/research-ideation/`
  * `.agents/skills/lit-review-assistant/`
  * `.agents/skills/working-with-data/`
  * `.agents/skills/python-panel-data/`
  * `.agents/skills/r-econometrics/`
  * `.agents/skills/stata-data-cleaning/`
  * `.agents/skills/stata-regression/`
  * `.agents/skills/econ-visualization/`
* **Attribution Note:** While CC0 1.0 does not legally require attribution, full credit and CC0 1.0 `LICENSE` files are preserved in every directory out of academic respect for the original authors.

---

## 3. Optional External Software & MCP Servers (Not Bundled)

This starter kit optionally integrates with the following separately installed tools under their own licenses:
* **Zotero Desktop & Local API** (AGPL-3.0, Corporation for Digital Scholarship) — <https://www.zotero.org/>
* **paper-search-mcp** — <https://github.com/openags/paper-search-mcp>
* **zotero-mcp** — <https://github.com/54yyyu/zotero-mcp>
* **notebooklm-mcp** & **openecon-data**

---

## MIT License Text (Applicable to Sections 2A & 2B)

```text
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
