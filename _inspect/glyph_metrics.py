#!/usr/bin/env python3
"""Glyph metrics needed for pixel-perfect tables."""
from fontTools.ttLib import TTFont

def metrics(path, chars):
    t = TTFont(path)
    upm = t["head"].unitsPerEm
    gs = t.getGlyphSet()
    cmap = t.getBestCmap()  # maps codepoint -> glyph NAME (string)
    hhea = t["hhea"]
    print(f"== {path.split('/')[-1]} (upm={upm}) ==")
    print(f"  hhea ascent={hhea.ascent} descent={hhea.descent} lineGap={hhea.lineGap}")
    print(f"  -> at 10pt: line={(hhea.ascent - hhea.descent + hhea.lineGap) / upm * 10:.3f}pt ascent={hhea.ascent / upm * 10:.3f}pt")
    os2 = t["OS/2"]
    print(f"  OS/2 typoAsc={os2.sTypoAscender} typoDesc={os2.sTypoDescender} typoGap={os2.sTypoLineGap}")
    for ch in chars:
        cp = ord(ch)
        if cp not in cmap:
            print(f"  {ch!r}: NOT IN FONT")
            continue
        gname = cmap[cp]                      # glyph name
        adv = gs[gname].width / upm * 10
        print(f"  {ch!r}: advance={adv:.3f}pt")

metrics("latex/fonts/MSGothic-Regular.ttf", ["\u2610", " "])
metrics("latex/fonts/Tahoma-Regular.ttf", [" ", "B", "P", "U", "N"])
metrics("latex/fonts/Tahoma-Bold.ttf", [" ", "A", "G"])