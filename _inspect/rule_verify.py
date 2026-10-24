#!/usr/bin/env python3
"""Rule-position verification: compare horizontal/vertical rule ink between
the reference render and our build (300dpi)."""
from PIL import Image

PPT = 3508 / 841.89

def load(img):
    p = Image.open(img).convert("L")
    return p, p.load()

def hline_span(px, x, y0, y1, thr=100):
    """first/last dark row at column x within (y0,y1) pt."""
    rows = [y for y in range(int(y0*PPT), int(y1*PPT)) if px[int(x*PPT), y] < thr]
    return (rows[0]/PPT, rows[-1]/PPT) if rows else None

def vline_span(px, y, x0, x1, thr=100):
    cols = [x for x in range(int(x0*PPT), int(x1*PPT)) if px[x, int(y*PPT)] < thr]
    return (cols[0]/PPT, cols[-1]/PPT) if cols else None

REF = "/home/cloude/from-word-to-latex/_inspect/hires-1.png"
MINE = "/home/cloude/from-word-to-latex/latex/myhires-1.png"

pr, pxr = load(REF)
pm, pxm = load(MINE)

print(f"{'rule':28s} {'REF span (pt)':>22s} {'MINE span (pt)':>22s}  dCenter")
checks = [
    ("T0 top", 200, 163, 167),
    ("T0 bottom", 200, 226, 229),
    ("T1 top", 200, 240, 243),
    ("T1 mid (0.5pt)", 200, 277, 280),
    ("T1 bottom", 200, 332, 335),
]
for name, x, ya, yb in checks:
    r = hline_span(pxr, x, ya, yb)
    m = hline_span(pxm, x, ya, yb)
    if r and m:
        rc, mc = (r[0]+r[1])/2, (m[0]+m[1])/2
        print(f"{name:28s} {r[0]:7.2f}..{r[1]:7.2f} {m[0]:7.2f}..{m[1]:7.2f}  {mc-rc:+7.2f}")
    else:
        print(f"{name:28s} ref={r} mine={m}")

print()
vchecks = [
    ("T0/T1 left border", 300, 60, 66),
    ("T0/T1 right border", 300, 528, 536),
    ("T1 divider", 250, 294, 301),
]
for name, y, xa, xb in vchecks:
    r = vline_span(pxr, y, xa, xb)
    m = vline_span(pxm, y, xa, xb)
    if r and m:
        rc, mc = (r[0]+r[1])/2, (m[0]+m[1])/2
        print(f"{name:28s} {r[0]:7.2f}..{r[1]:7.2f} {m[0]:7.2f}..{m[1]:7.2f}  {mc-rc:+7.2f}")
    else:
        print(f"{name:28s} ref={r} mine={m}")