# Plan: LaTeX Replication of `01_Ansuchen Zuteilung wiss Arbeit.docx`

**Goal:** produce `ansuchen.tex` (XeLaTeX) whose PDF is visually identical to the
FH-Burgenland Word form — same fonts, same page geometry, same table layout,
same logo placement, same footer block.

**Fidelity oracle:** the LibreOffice-rendered reference PDF
(`_inspect/01_Ansuchen Zuteilung wiss Arbeit.pdf`, 2 pages, A4) rendered with
the docx's own embedded fonts. Word itself may differ by a hair; LibreOffice's
render is our measurable ground truth (page images: `_inspect/page-1.png`,
`page-2.png`, hi-res `_inspect/hires-1.png`).

---

## 0. Status of preparation work (already done, verified)

| Asset | Path | Status |
| --- | --- | --- |
| Embedded fonts (deobfuscated from `.odttf`, validated with fontTools) | `latex/fonts/Tahoma-Regular.ttf`, `Tahoma-Bold.ttf`, `GillSansMT-Regular.ttf`, `Cambria-Regular.ttf`, `MSGothic-Regular.ttf`, `BookAntiqua-Regular.ttf` | ✅ extracted, magic bytes + fontTools OK |
| Logo (cropped to visible alpha bbox, 1105×402 px, aspect 2.749) | `latex/assets/fh-logo.png` | ✅ extracted |
| Reference PDF + page PNGs + `pdftotext -bbox` dump | `_inspect/` | ✅ generated |
| Raw XML of docx (unzipped) | `_inspect/word/` | ✅ available for double-checks |

Deobfuscation method that worked (kept here for reproducibility):
XOR the first 32 bytes of each `font*.odttf` with the reversed little-endian
bytes of its `w:fontKey` GUID (`uuid.UUID(key).bytes_le[::-1]`, repeating
16-byte key).

---

## 1. Document analysis summary

- **Producer:** FH-Burgenland official form (PQMS-controlled, `LE0400_DEPI_V_01`,
  v1.1), author "Freyer Nadine", Word for the web.
- **Body structure (element order):**
  1. Title: *Ansuchen um Zuteilung einer wissenschaftlichen Arbeit* — Tahoma bold 12 pt
  2. *Department Informationstechnologie* — Tahoma 10 pt
  3. **Table T0** — degree-type picker (1 col, checkbox rows)
  4. empty para
  5. **Table T1** — student name / PKZ / Datum / Unterschrift (2×2)
  6. empty para
  7. **Table T2** — Arbeitstitel + Themenquelle + inline footnote (2×1)
  8. empty para
  9. **Table T3** — Genehmigung durch die Studiengangsleitung (3×3, merged)
  10. empty para → **page break happens here naturally** (page 2)
  11. *Themendisposition* (bold 12 pt) + *Ausführliche Darstellung … (2-3 Seiten)* (10 pt)
  12. **Table T4** — 8 full-width labeled writing rows
  13. empty para
- **No** tracked changes, no real footnotes (the "¹" note is inline text at the
  bottom of T2), no comments, no hyperlinks, no headings/TOC, no numbering.
- **Fonts used in render:** Tahoma (regular + bold) for everything except the
  checkbox glyphs; ☐ (U+2610) is MS Gothic 10 pt. Gill Sans MT is declared as
  the Normal-style font but every run overrides with the theme minor font
  (= Tahoma), so **the document is effectively 100 % Tahoma**. Footer is 6 pt
  Tahoma, colour `#808080`, lines 1–2 bold.
- **Checkbox glyphs:** 15 × `☐` U+2610, each wrapped in a Word content control
  (`w:sdt`), font MS Gothic, sz 20 half-points (=10 pt). Rendered ≈ 10 pt wide.

---

## 2. Measured page geometry (ground truth)

A4 595.3 × 841.9 pt. 1 cm = 28.346 pt.

| Property | Value |
| --- | --- |
| Margins | top 4.44 cm (125.9 pt), bottom 2.25 cm, left/right 2.20 cm |
| Header distance | 1.25 cm; header contains **only** the floating logo (no text) |
| Footer distance | 1.19 cm; 4 text lines land at y ≈ 779.1 / 786.4 / 793.6 / 800.9 pt (7.3 pt pitch) |
| Text column | 62.6 → 532.6 pt (470 pt = 16.58 cm) |
| Default tab stops | 1.25 cm grid (Word default, `w:defaultTabStop=708`) |

**Logo (floating, in header, repeats on both pages):** visible content occupies
x = 61.9→198.6 pt (2.18→7.01 cm), y = 46.1→95.7 pt (1.62→3.38 cm from top);
rendered size **4.82 × 1.75 cm**. (In OOXML it's a 9.9 cm image anchored at
column −2.807 cm / paragraph −3.51 cm, but only the visible bbox matters —
we place the cropped PNG at the measured page coordinates.)

**Title block:** title text top at y = 126 pt (exactly the top margin),
"Department Informationstechnologie" at y = 146 pt (20 pt line pitch).

---

## 3. Measured table geometry

All tables: outer borders **1.5 pt** (`sz=12`), inner borders **0.5 pt** (from
`Tabellenraster`/Table-Grid style, `sz=4`), black. Table width = full text
width 16.55 cm. Cell side padding = Word default 0.19 cm (5.4 pt) → set
`\tabcolsep = 5.4pt`. No cell margins/indent overrides.

Horizontal rule positions (page 1): T0 top 164.8, T0 bottom 227.4, T1 top
241.1, T1 mid 277.8, T1 bottom 333.9, T2 top 346.8, T2 mid 414.5, T2 bottom
658.4, T3 top 672.8, T3 r1 698.0, T3 r2 716.7, T3 bottom 772.1.
Page 2, T4: tops at 195.0, 261.2, 326.7, 392.9, 459.1, 525.3, 591.5, 657.0,
bottom 723.2 → **row pitch exactly 66.15 pt (2.335 cm)**.
Vertical rules: table left edge x=63.3, right edge x=532.0; T1/T3 mid divider
x=297.3 (8.27 cm column split); T3 also has a divider at x ≈ 203.8 (4.98 cm).

### T0 — degree picker (1 row × 1 col)
Three lines inside the cell, 6 pt space-before between them (~18.4 pt pitch):
1. `Bitte wählen:` — Tahoma 10
2. `☐ Bachelorarbeit  ☐ BIMK  ☐ BITI  ☐ BSWE  ☐ BWIF`
3. `☐ Masterarbeit  ☐ MASE  ☐ MBPM  ☐ MCCE  ☐ MDMK  ☐ MEWM`

Rendered x-positions of the ☐ glyphs: 68.6 (cell text start, no tab),
then 174.8 / 245.6 / 316.4 / 387.2 / 458.0 pt → first gap 106.8 pt (3.77 cm
from cell text origin), then every **70.8 pt = 2.5 cm**.
Labels follow each box with ~3 pt gap. All labels Tahoma 10 pt.
Row 2 labels start at x=81.7 (i.e. box + space + text at ~13 pt offset).

### T1 — student data (2×2, grid 8.27 + 8.27 cm)
- r0 (241.1→277.8, ≈ 36.7 pt): `Name der/des Studierenden:` | `PKZ:` (Tahoma 10)
- r1 (277.8→333.9, ≈ 56.1 pt, blank writing space): left cell has 2 empty paras
  then `Datum` at y=315 (i.e. ~18 pt above the bottom rule); right cell has
  `Unterschrift` alone at the top of the row.
- insideV at x=297.3 (0.5 pt), horizontal rules 1.5 pt outer / 0.5 pt mid.

### T2 — Arbeitstitel / Themenquelle (2 rows × 1 col)
- r0 (346.8→414.5, ≈ 67.7 pt): label `ersucht um Zuteilung einer wissenschaftlichen
  Arbeit mit dem Arbeitstitel (und Aufgabenbereich bei Gruppenarbeiten)` (wraps
  to 2 lines, y=348/360) + 2 empty paras of writing space.
- r1 (414.5→658.4, ≈ 243.9 pt), content (all Tahoma 10, line pitch ~18 pt):
  | y | content | x of first glyph |
  | --- | --- | --- |
  | 415 | `Themenquelle:` | 68.6 |
  | 433 | `☐ a) Vorschlag des/der Studierenden` | ☐ at 104.0 (1.27 cm), `a)` at 117.1 |
  | 451–463 | `Die Bearbeitung der Fragestellung erfolgt … einer externer Institution¹` (2 lines, left-indented 2.54 cm → x=140.7; ¹ superscript) | 140.7 |
  | 481 | `☐ ja` | ☐ at 174.8 (3.77 cm), `ja` at 187.9 |
  | 499 | `☐ nähere Angaben:` | ☐ at 174.8, text at 187.9 |
  | ~524/549/574 | 3 blank writing lines (~25 pt pitch) | — |
  | 574 | `☐ nein` | ☐ at 174.8 |
  | 592 | `☐ b) Vorschlag des Studienganges` | ☐ at 104.0 |
  | 628–640 | `¹ Als externe Unternehmen oder externe Institutionen gelten alle Unternehmen oder Institutionen außer der Hochschule für Angewandte Wissenschaften Burgenland GmbH` (superscript ¹ then 2 wrapped lines, x=68.6) | 68.6 |

### T3 — Genehmigung (3 rows, grid 4.98 + 3.29 + 8.27 cm)
- r0 (672.8→698.0, 25.2 pt): full-width merged cell, **bold** `Genehmigung durch
  die Studiengangsleitung` (10 pt, y=680)
- r1 (698.0→716.7, 18.7 pt): `Zugewiesene*r Betreuer*in:` in col 1, cols 2–3
  merged + empty
- r2 (716.7→772.1, 55.4 pt): cols 1–2 merged with `Datum` near bottom (y=753);
  col 3 has `Unterschrift` at top (y=753 in render — same line).
  (Declared trHeights 264/263 twips are minimums; the render is authoritative.)

### T4 — Themendisposition (8 rows × 1 col, page 2)
Rows of exactly 66.15 pt (2.335 cm), each containing a bold 10 pt label at the
top (6 pt space-before, label y = row top + 7 pt) + blank writing space:
1. `Ausgangssituation & Problemhintergrund`
2. `Wissenschaftliche Fragestellung`
3. `Ziel sowie Nutzen der Arbeit`
4. `Nicht-Ziele`
5. `Forschungsmethodik`
6. `Grobgliederung mit Seitenbudgets`
7. `Zeitplan`
8. `Bislang herangezogene Literatur`

Headings above it (page 2): `Themendisposition` bold 12 pt at y=152,
`Ausführliche Darstellung der eingereichten Fragestellung (2-3 Seiten)` 10 pt
at y=175 (6 pt space-before each).

---

## 4. Footer block (both pages)

4 lines, Tahoma 6 pt, colour `#808080`, baseline pitch 7.3 pt; lines 1–2 bold:

| # | Rendered | Layout |
| --- | --- | --- |
| 1 | `1/2` at y=779.1 | **dynamic**: `PAGE`/`NUMPAGES` fields → `\thepage/\pageref{LastPage}`, right-aligned to 16.5 cm stop (ends x=530.3) |
| 2 | `LE0400_DEPI_V_01 Ansuchen Zuteilung wiss Arbeit` … `PQMS` (bold) | left text at margin + `PQMS` right-aligned at 16.5 cm |
| 3 | `KP01 – Studium & Lehre` … `Version 1.1 - zuletzt geändert: 19.11.2024/hos` | left text + right-aligned tail (ends x=530.1) |
| 4 | `erstellt: 09.03.2022/frn` … `geprüft: 09.03.2022/buc` … `freigegeben: 19.11.2024/buc` | left; `geprüft:` starts at x=256.9 (6.86 cm); `freigegeben:` right-aligned (ends 530.1) |

(The docx caches the stale field value `3/3`; the real render shows `1/2` —
replicate the live fields, i.e. `1/2`, `2/2`.)

---

## 5. LaTeX implementation strategy

### Engine & packages
- **XeLaTeX** (TTF fonts loaded directly via fontspec; Tahoma is a TrueType
  font — pdflatex would need lossy conversion).
- Packages: `geometry`, `fontspec`, `xcolor`, `array`, `tabularx`, `calc`,
  `fancyhdr`, `lastpage`, `eso-pic`, `graphicx`, `setspace`.

### Preamble skeleton

```latex
\documentclass[a4paper]{article}
\usepackage[a4paper, top=4.44cm, bottom=2.25cm, left=2.2cm, right=2.2cm,
            includefoot, footskip=6pt, headheight=12pt, headsep=0.5cm]{geometry}
\usepackage{fontspec}
\setmainfont{Tahoma}[Path = fonts/, Extension = .ttf,
  UprightFont = *-Regular, BoldFont = *-Bold]
\newfontfamily\msgothic{MSGothic}[Path = fonts/, Extension = .ttf]  % ☐ U+2610
\usepackage{xcolor,graphicx,array,tabularx,calc,fancyhdr,lastpage,eso-pic}
\definecolor{footergrey}{HTML}{808080}
\setlength{\tabcolsep}{5.4pt}      % Word default cell side padding 0.19 cm
\newcommand{\cbx}{\msgothic\char"2610}  % MS Gothic 10 pt ballot box
% thick outer rules 1.5pt / thin inner rules 0.5pt:
\newcommand{\TWr}{\noalign{\hrule height 1.5pt}}   % thick horizontal rule
\newcommand{\tnr}{\noalign{\hrule height 0.5pt}}   % thin horizontal rule
% vertical: |!{\vrule width 1.5pt}|
```

### Logo (repeats every page)
Absolute placement of the cropped PNG at the measured page coordinates
via `eso-pic` (origin = page upper-left, y grows downward):

```latex
\AddToShipoutPictureBG{%
  \AtPageUpperLeft{\put(2.18,1.62){%          % cm from page top-left
    \includegraphics[width=4.82cm]{assets/fh-logo.png}}}
```
(4.82 cm wide → height 1.75 cm automatically; aspect 2.749 preserved.)

### Footer
Empty header. Footer = one left-aligned `tabular` in `\fancyfoot[L]` with
`\footnotesize`-free explicit `\fontsize{6}{7.3}\selectfont\color{footergrey}`
and `\hfill`-style right alignment; first row =
`{\bfseries\thepage/\pageref{LastPage}}\hfill` pattern with right edge at
16.5 cm (use `\makebox[16.5cm][r]{…}` trick per row or a 3-column tabular
with fixed widths). Rows 2 bold, 3–4 regular. Tune `footskip` until row 1
baseline ≈ 784 pt (QA loop verifies).

### Tables
- Use plain `tabular`/`tabularx` with `p{}` columns; mixed rule weights via the
  `\TWr`/`\tnr` macros above and `!{\vrule width 1.5pt}` for outer verticals,
  `|` (0.4 pt ≈ 0.5 pt, or set `\arrayrulewidth=0.5pt`) for inner verticals.
- **T0 checkbox lines:** one tabular row per line with fixed-width columns:
  first column 3.77 cm, following columns 2.5 cm each, each cell
  `\cbx\, LABEL` (Tahoma). Or simpler: `\makebox`-chains at the measured x
  positions. Verify ☐ glyph advance ≈ 10 pt; if MS Gothic's advance differs,
  add `\hspace` compensation or `Scale=` in fontspec.
- **T1:** 2 equal `p{8.27cm}` columns; r1 = fixed-height cell
  (`\parbox[b][56.1pt][t]{...}` or `p{}` + `\vspace*{38pt}` before `Datum`)
  so the row is exactly 56.1 pt.
- **T2:** single `p{16.55cm}` column; replicate the two rows; inside r1 use
  `\hspace*{1.27cm}` / `\hspace*{3.77cm}` for the ☐ positions (or tab stops:
  `\setlength{\DPtab}{}` with `tabto`-style stops at 1.27 / 3.77 / +2.5 cm),
  `\hspace*{2.54cm}` block indent, `\textsuperscript{1}` markers, footnote
  paragraph at cell bottom. Three blank writing lines ≈ 25 pt pitch between
  `nähere Angaben:` and `☐ nein`.
- **T3:** `tabular` with columns 4.98 / 3.29 / 8.27 cm; r0 = `\multicolumn{3}`,
  r1 = col 1 + `\multicolumn{2}{2}`, r2 = `\multicolumn{2}` + col 3; heights
  25.2 / 18.7 / 55.4 pt (struts `\rule{0pt}{…}` or parbox).
- **T4:** 8 rows; each = bold label + vertical fill to exactly 66.15 pt:
  `p{16.58cm}` cell = `\textbf{Label}\vspace*{...}` inside
  `\parbox[t][66.15pt][t]{16.58cm}{...}`. Bold = Tahoma Bold.

### Inter-table gaps & pagination
Empty paragraphs between tables: T0→T1 13.7 pt, T1→T2 12.9 pt, T2→T3 14.4 pt
(rendered values) → `\vspace` between tabulars (or empty `\parbox`es). After T3
insert `\newpage` if the natural break doesn't land identically (in Word the
break is natural because only ~6 pt remain; verify — if XeLaTeX also breaks
naturally at the same element, keep it natural). Page 2 headings: 6 pt
space-before each, 12 pt bold / 10 pt regular.

### Build command

```bash
cd latex && xelatex -interaction=nonstopmode ansuchen.tex   # run twice (lastpage)
```

---

## 6. QA loop (must pass before "done")

1. **Text integrity:** `pdftotext` of our PDF must contain every string from
   §3/§4 exactly (umlauts, `–` en-dash, `*` in `Zugewiesene*r Betreuer*in:`).
2. **Coordinate diff:** run `pdftotext -bbox` on both PDFs; script pairs every
   word and reports max Δx/Δy. **Acceptance: ≤ 2 pt** for every word, table
   rule positions ≤ 2 pt, logo bbox ≤ 3 pt.
3. **Pixel diff:** render both at 150 dpi; ImageMagick `compare -metric AE` or
   PIL `ImageChops.difference`. **Acceptance: < 3 % differing pixels** (excluding
   anti-aliasing noise, e.g. blur-tolerant diff).
4. **Page count = 2**; page 2 starts with `Themendisposition`.
5. **Fonts:** `pdffonts latex/ansuchen.pdf` must list embedded Tahoma / Tahoma
   Bold / MS Gothic (subset-embedded) — no fallback fonts.
6. Iterate: fix geometry (tabcolsep, strut heights, footskip, vspace) → rebuild
   → re-diff, until all four checks pass.

Suggested QA helper (to write during implementation): `latex/qa_diff.py` that
parses two `pdftotext -bbox` HTML files and prints a per-word deviation table
sorted worst-first.

---

## 7. Target file layout

```
from-word-to-latex/
├── 01_Ansuchen Zuteilung wiss Arbeit.docx   (source, untouched)
├── PLAN.md                                  (this file)
├── README.md
├── .gitignore
├── scripts/
│   └── extract_fonts.py                     (re-extract embedded fonts + logo from the docx)
├── latex/
│   ├── ansuchen.tex                         (the deliverable)
│   ├── assets/fh-logo.png                   ✅ done
│   └── fonts/*.ttf                          ✅ done — gitignored (font licensing; rebuild via scripts/extract_fonts.py)
└── _inspect/                                (analysis artifacts + reference PDF)
```

## 8. Risks & fallbacks

| Risk | Fallback |
| --- | --- |
| MS Gothic ☐ advance/size differs in fontspec | use `\framebox[7.5pt]{\rule{0pt}{7.5pt}}`-style drawn box, or DejaVu Sans `U+2610` with `Scale=` — visually indistinguishable at 10 pt |
| Footer multi-line positioning fights fancyhdr | place the whole footer via `eso-pic` shipout block at absolute y ≈ 779 pt |
| Natural page break differs | force `\newpage` before `Themendisposition` |
| `tabularx` stretching vs fixed grid | all columns are fixed-width `p{}`/`parbox` anyway — no stretching used |
| Font licensing | fonts come from the user's own docx (embedded by FH-Burgenland); local personal-use rendering only — no redistribution |

### LaTeX-specific gotchas discovered during Phase 2 (all fixed, keep for reference)

- **TeX pt ≠ PDF bp.** Word measurements and pdftotext output are in PDF
  points (bp, 72/in). TeX `pt` is 72.27/in → a −0.36% *gradient* across the
  page. Use `bp` everywhere: `\fontsize{10bp}{12.07bp}`, `\rule{…bp}`,
  `\setlength{\unitlength}{1bp}`. Symptom: errors growing linearly with
  distance from origin.
- **`\rule` grows UP from its anchor** (reference point = bottom-left). To
  place a rule whose top edge is at depth d with thickness t, put its bottom
  at d+t: `\put(x,-(d+t)){\rule{w}{t}}`.
- **pdftotext word boxes are layout line boxes**, not ink. baseline =
  yMin + k·(yMax−yMin) with renderer-specific k (LibreOffice Tahoma ≈ 0.829,
  XeTeX ≈ 0.741, MS Gothic ≈ 0.859). `qa_diff.py` converts to baselines
  before comparing.
- **Flow-mode anchoring (topskip/baselineskip) is unreliable** for
  exact-placement work — shipout-layer (`eso-pic` + `\AtPageUpperLeft`) is
  deterministic and matches the footer/logo mechanism.
- **A `\put` outside a picture environment silently typesets nothing**
  (no log error). Always wrap content macros in `\AtPageUpperLeft{…}`.
- **Frame anchor** (shipout layer, bp): origin = (63, −126.40) from the page
  top-left — 63 = left rule center x; 125.95 = Word top margin, +0.45
  empirical correction.

## 9. Execution checklist

- [x] Phase 0 — extract & validate fonts, crop logo, generate reference PDF/PNGs, measure everything (this document)
- [x] Phase 1 — `ansuchen.tex` skeleton: geometry, fonts, logo, footer, page numbering; compile clean
- [x] Phase 2 — T0 + T1 with exact columns/heights; QA pass on their region
      (0/94 words beyond 2pt, worst 0.76pt; rules within ±0.24pt; shipout-layer
      absolute placement, bp units, baseline-aware qa_diff)
- [ ] Phase 3 — T2 (indents, checkboxes, inline footnote) + T3 (merges)
      ✅ DONE: 0/172 words beyond 2pt; all T2/T3 rules at +0.00pt ink-delta;
      T3 row-1 divider (204.35) + Unterschrift divider (297.47) only span
      their rows (merged-cell geometry); anchor fixed to true -125.95 Word
      top margin; superscript ¹ placed at 5.79bp explicit font size
- [ ] Phase 4 — page-2 headings + T4 fixed-pitch rows
- [ ] Phase 5 — full QA loop (bbox + pixel diff), fix deviations, final report