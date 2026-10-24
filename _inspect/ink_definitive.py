#!/usr/bin/env python3
"""Definitive: tight-crop ink measurement of MY render vs REFERENCE render for
no-descender words in T0/T1, avoiding any rule pollution."""
from PIL import Image

PPT = 3508 / 841.89  # both renders are 2481x3508 @300dpi

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

# tight crops that CANNOT touch rules:
crops = {
    # word, (x0,y0,x1,y1) tight around the word, away from rules
    "Bitte (T0L1)": (69.0, 174.0, 126.0, 184.5),
    "wählen: (T0L1)": (91.5, 174.0, 130.0, 187.0),
    "BIMK (T0L2)": (189.0, 193.5, 211.0, 203.5),
    "MEWM (T0L3)": (471.5, 211.5, 501.5, 221.5),
    "Name (T1r0)": (66.5, 242.5, 96.0, 254.5),
    "PKZ: (T1r0)": (300.0, 242.5, 330.0, 254.5),
    "Datum (T1r1)": (69.0, 318.0, 95.0, 329.5),
    "Unterschrift (T1r1)": (304.0, 318.0, 345.0, 329.5),
}
print(f"{'word':22s} {'MY ink y':>18s} {'REF ink y':>18s}  dy(base)")
for w, (x0, y0, x1, y1) in crops.items():
    m = ink(MINE, x0, y0, x1, y1)
    r = ink(REF, x0, y0, x1, y1)
    if m and r:
        # bottom of ink = baseline for caps/no-descender words (choose same word)
        dy = m[3] - r[3]
        print(f"{w:22s} {m[1]:7.2f}..{m[3]:7.2f} {r[1]:7.2f}..{r[3]:7.2f}  {dy:+.2f}")
    else:
        print(f"{w:22s} my={m} ref={r}")