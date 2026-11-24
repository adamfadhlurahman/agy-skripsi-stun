---
name: pkn-stan-thesis-writer
description: Drafts and audits PKN STAN thesis proposals and complete theses across all departments/programs in strict compliance with PER-9/PKN/2020 formatting, PER-4/PKN/2020 anti-plagiarism limits, 4 official research archetypes, APA 7th citations, and live Zotero Word fields.
---

# PKN STAN Thesis Writer & Style Guard (`PER-9/PKN/2020` & `PER-4/PKN/2020`)

This skill enforces physical typography, complete front-to-back manuscript structure across all PKN STAN study programs, formal Indonesian/academic prose rules, APA 7th Edition citation mechanics, plagiarism prevention, and live Zotero Word field integration.

---

## 1. Mandatory Physical Format & Typography (`PER-9/PKN/2020` Annex I Ch. I)

* **Paper & Margins:** A4 (`21 x 29.7 cm`). Left **`4 cm`**, Top **`4 cm`** (first page of every new Chapter / major front-matter heading: Top **`7.5 cm`**), Right **`3 cm`**, Bottom **`3 cm`**. Body text is **justified**.
* **Font (`Times New Roman`):**
  * Normal body prose: `12 pt`, upright, **`2.0` line spacing**, first-line paragraph indent **`1.27 cm`** (`0.5 inch`).
  * `BAB X` & `JUDUL BAB`: `14 pt`, **ALL CAPS BOLD**, centered. Spacing between `BAB X` and `JUDUL BAB` is `2.0`; spacing before first body/subheading line is `3.0`.
  * Level 2 (`## 1.1`): `12 pt`, **Bold**, Title Case, **no trailing period**.
  * Level 3 (`### 1.1.1`): `12 pt`, **Bold**, Title Case, **no trailing period**.
  * Level 4 (`#### 1.1.1.1`): `12 pt`, regular (non-bold), Title Case, **no trailing period**.
  * Level 5 (`##### 1.1.1.1.1`): `12 pt`, regular, sentence case, **ends with a period**.
* **Single (`1.0`) Spacing Exceptions:** Long direct quotes (> 4 lines, indented `1.27 cm` left & right via Markdown blockquote `> ...` mapped to `Kutipan Langsung`), footnotes (`1.5` spacing between notes), table cells, TOC/List of Tables/Figures/Appendices entries (blank line between main items), Abstract (`1.0` spacing), and within individual Reference entries (`2.0` spacing between entries).
* **Page Numbering:**
  * Front matter uses lowercase Roman numerals (`i, ii, iii...`) at **top-right** (cover/title page unnumbered).
  * Main body & back matter use Arabic numerals (`1, 2, 3...`): **bottom-center** (`1.5 cm` from bottom) on the first page of each Chapter/major section, and **top-right** (`3 cm` from right, `1.5 cm` from top) on all subsequent pages.
* **Tables & Figures (`PER-9` 1.12):**
  * Number & caption **centered above** the table/figure (e.g., `Tabel II.1 ...`, `Gambar IV.1 ...`).
  * In-text references must cite the exact number (`Tabel IV.1`, `Gambar II.1`)—**never** use *"tabel di atas"* or *"gambar di bawah ini"*.
  * Source line **below**: `"Sumber: ..."` if direct, `"Sumber: Diolah dari ..."` if processed from external data, or `"Sumber: Diolah penulis"` if self-constructed.
  * List of Tables, List of Figures, and List of Appendices are required whenever there are 3 or more items in each category (`PER-9` 3.1.1.2).

---

## 2. Complete Proposal & Thesis Structure (`PER-9/PKN/2020` Ch. II & III)

### A. Thesis Proposal Structure (`PER-9` 2.1–2.2)
1. Front Matter: Title Page (Cover), Proposal Approval Page (`PERSETUJUAN PROPOSAL SKRIPSI`), Table of Contents (+ Lists of Tables/Figures/Appendices if applicable).
2. Main Body: Chapter I Introduction, Chapter II Literature Review, Chapter III Research Methodology (or archetype equivalent).
3. Back Matter: References + Research Schedule Appendix (+ survey/interview instruments if applicable).

### B. Complete Thesis Structure (`PER-9` 3.1.1–3.1.3)
* **Recommended Word Count (`3.1.2.2`):** **`5,000` to `20,000` words** across Chapters I–V.
* **Front Matter Order (`3.1.1.1`):**
  1. Title Page (unnumbered)
  2. Thesis Approval Page (`PERSETUJUAN SKRIPSI`)
  3. Examination Pass Statement (`PERNYATAAN LULUS DARI TIM PENILAI SKRIPSI`, for examined theses)
  4. Statement of Originality (`PERNYATAAN KEASLIAN SKRIPSI`)
  5. Preface / Acknowledgments (`KATA PENGANTAR`)
  6. Table of Contents (`DAFTAR ISI`)
  7. List of Tables (`DAFTAR TABEL`, if >= 3)
  8. List of Figures (`DAFTAR GAMBAR`, if >= 3)
  9. List of Appendices (`DAFTAR LAMPIRAN`, if >= 3)
  10. Abstract (`ABSTRAK`, max **`250` words**, `1.0` spacing, with `Kata kunci`)
* **Main Body (`3.1.2.1`) — 4 Official PKN STAN Archetypes:**
  1. **Quantitative (Descriptive or Causal):** `PENDAHULUAN` -> `LANDASAN TEORI` -> `METODE PENELITIAN` -> `HASIL PENELITIAN DAN PEMBAHASAN` -> `SIMPULAN DAN SARAN`.
  2. **Qualitative (Case Study or Non-Case Study):** `PENDAHULUAN` -> `LANDASAN TEORI` -> `METODE PENELITIAN` -> `HASIL PENELITIAN DAN PEMBAHASAN` -> `SIMPULAN DAN SARAN`.
  3. **Descriptive Simulation:** `PENDAHULUAN` (incl. methodology) -> `LANDASAN TEORI` (incl. operational criteria) -> `INTI PENELITIAN` -> `HASIL PENELITIAN DAN EVALUASI` -> `SIMPULAN DAN SARAN`.
  4. **Descriptive Design (System Engineering):** `PENDAHULUAN` (incl. methodology) -> `LANDASAN TEORI` (incl. design methodology & tools) -> `ANALISIS SISTEM YANG BERJALAN` -> `RANCANGAN SISTEM YANG DIUSULKAN` -> `SIMPULAN DAN SARAN`.
* **Back Matter Order (`3.1.3`):**
  1. References / Bibliography (`DAFTAR PUSTAKA`)
  2. Appendices (instruments, schedules, supporting tables)
  3. Research Permit Letter (if applicable)
  4. Author Curriculum Vitae (`DAFTAR RIWAYAT HIDUP`)

---

## 3. Formal Academic Prose & Anti-Plagiarism Rules (`PER-9` 1.7–1.9 & `PER-4/PKN/2020`)

* **No First/Second-Person Pronouns (`PER-9` 1.9.1):** Never use `saya`, `aku`, `kita`, `kami`, or `Anda`. Use formal passive voice or **`penulis`** if agency must be named.
* **Indonesian Academic Prose Hygiene (`PER-9` 1.9.3 + `humanizer-indonesia`):**
  1. Never begin a sentence with `Sedangkan`, `Sehingga`, `Dan`, `Atau`, or `Konsekuensinya`.
  2. Never use `di mana`, `dimana`, or `yang mana` as relative connectors in declarative sentences.
  3. Use `antara lain` instead of `di antaranya`.
  4. Italicize unassimilated foreign terms and introduce acronyms on first use.
  5. **Zero em-dashes (`—`) or en-dashes (`–`) in prose body** (en-dash allowed only in numeric ranges like `2023–2025` or page ranges).
  6. Use `jika`/`apabila` instead of `bila`, standard KTSP nasalization (`memengaruhi`, `menyintesis`, `mengubah`), and KBBI spelling (`analisis`, `risiko`, `efektivitas`, `standardisasi`, `tolok ukur`, `linear`, `objek`).
  7. No spaces inside parentheses: `(APBN)`.
* **Turnitin Similarity Limit (`PER-4/PKN/2020` Art. 6 & 9):** Maximum **30%** across Chapters I–V (excluding References and Appendices), with direct quotes <= 50% per page. Synthesize and paraphrase fully from primary sources; never copy raw prose from external papers or previous KTTA drafts.

---

## 4. APA 7th Edition Citations & Live Zotero Fields (`PER-9` 1.10–1.11)

* **Never use footnotes for citations** (footnotes are strictly for substantive side notes).
* **Two authors:** use **`dan`** in narrative citations (`Subramanyam dan Wild (2008)`), and **`&`** inside parentheses (`(Subramanyam & Wild, 2008)`).
* **Three or more authors:** use `dkk.` (for `id-ID` locale) or `et al.` consistently throughout.
* **Secondary citations:** `(Keynes, 1931, dikutip dalam DeLong & Olney, 2006, hlm. 389)` — always prefer primary sources.
* **Live Zotero Integration:** Register all cited sources in the student's Zotero collection (`03. Drafts/zotero_map.json`). `scripts/build_thesis_docx.py` injects native `ADDIN ZOTERO_ITEM CSL_CITATION {...}`, `ZOTERO_PREF_1`, and `ADDIN ZOTERO_BIBL` so **Zotero -> Refresh** in Word works live.
