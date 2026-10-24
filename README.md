# from-word-to-latex

Recreating an FH-Burgenland Word form (`01_Ansuchen Zuteilung wiss Arbeit.docx`)
as a pixel-faithful LaTeX document.

## Status

- **[PLAN.md](PLAN.md)** — full analysis of the source document + measured
  geometry + implementation strategy + QA loop. Start here.
- `latex/ansuchen.tex` — the XeLaTeX deliverable (planned, see PLAN.md §9).
- `_inspect/` — analysis artifacts (reference PDF, page renders, inspection
  scripts and dumps used to produce the measurements in PLAN.md).

## Quick start

```bash
# 1. extract embedded fonts + logo from the docx (needs Pillow)
python3 scripts/extract_fonts.py

# 2. build (TeX Live 2026, XeLaTeX)
cd latex && xelatex ansuchen.tex && xelatex ansuchen.tex
```

## Why the fonts are not committed

The source docx embeds Tahoma, Cambria, MS Gothic, Book Antiqua and Gill
Sans MT (Microsoft/Monotype fonts). They are extracted locally for rendering
fidelity only — the repo ships just the extraction script
(`scripts/extract_fonts.py`) to keep licensed binaries out of the public
repository.