#!/usr/bin/env python3
"""Ink-baseline measurement for title/dept lines (both renders, 300dpi).
These anchor the whole flow-chain correction."""
from PIL import Image

PPT = 3508 / 841.89

def ink(img, x0, y0, x1, y1, thr=128):
    p = Image.open(img).convert("L")
    px = p.load()
    X0, Y0, X1, Y1 = [int(v * PPT) for v in (x0, y0, x1, y1)]
    b = [None, None, None, None]
    for y in range(Y0, Y1):
        for x in range(X0, X1):
            if px[x, y] < thr:
                b[0] = x if b[0] is None else min(b[0], x)
                b[1] = y if b[1] is None else min(b[1], y)
                b[2] = x if b[2] is None else max(b[2], x)
                b[3] = y if b[3] is None else max(b[3], y)
    return [v / PPT for v in b] if b[0] is not None else None

MINE = "/home/cloude/from-word-to-latex/latex/myhires-1.png"
REF = "/home/cloude/from-word-to-latex/_inspect/hires-1.png"

# bands that avoid all rules (first rules start at y≈164)
probes = {
    "title 'Ansuchen um' (x 62-100)": (62, 127, 100, 141),
    "title 'Arbeit' end (x 425-470)": (425, 127, 470, 141),
    "dept 'Department' (x 62-120)": (62, 146, 120, 160),
    "dept end 'gie' (x 240-290)": (240, 146, 290, 160),
}
for name, (x0, y0, x1, y1) in probes.items():
    m = ink(MINE, x0, y0, x1, y1)
    r = ink(REF, x0, y0, x1, y1)
    print(f"{name:38s} MY y={m[1]:.2f}..{m[3]:.2f}  REF y={r[1]:.2f}..{r[3]:.2f}  dy(base)={m[3]-r[3]:+.2f} dx={m[0]-r[0]:+.2f}")

# 'Arbeit' title word: 'A' has no descender; title line caps bottom = baseline
# dept 'Informationstechnologie': 'g' HAS a descender! use bottom = baseline+desc
# For dept use a band without descenders: 'Department' has 'p' descender...
# 'Informationstechnologie' has 'g'. Whole dept line: use TOP instead (caps top):
# caps top of 'D' = baseline - capsheight. Simpler: compare SAME band for both
# renders (dy of ink top = dy of baseline for identical glyph sets).