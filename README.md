# from-word-to-latex

Recreating an FH-Burgenland Word form (`01_Ansuchen Zuteilung wiss Arbeit.docx`)
as a pixel-faithful LaTeX document.

## Status: COMPLETE ✅

The full 2-page form is replicated and QA-verified against the LibreOffice
reference render:

- **Words:** 191/191 within 2pt (worst baseline delta 0.18pt; ink-truth
  measurement +0.06pt mean)
- **Rules:** all 25 table rules ink-verified at 300dpi (worst 0.24pt = 1px)
- **Pixel diff:** 0.82% (page 1) / 1.18% (page 2), target <3%
- **Fonts:** the docx's own embedded fonts (Tahoma R/B, MS Gothic for ☐),
  deobfuscated from `.odttf` and re-embedded via fontspec
- Live `PAGE/NUMPAGES` footer numbers, floating logo on both pages

See **[PLAN.md](PLAN.md)** for the full measured-geometry analysis, the
implementation strategy, and the QA methodology.

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