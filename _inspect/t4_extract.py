#!/usr/bin/env python3
"""Phase 4 extraction: T4 (page 2) rule positions at 300dpi + label baselines
from the vector bbox. Outputs LaTeX-ready numbers (depths rel. Word top
125.95pt = frame origin -125.95; x rel. 63pt)."""
import re
from PIL import Image

BASE = "/home/cloude/from-word-to-latex/"

# ---------- 1) rules from 300dpi render of reference page 2 ----------
p = Image.open(BASE + "_inspect/hires-2.png").convert("L")
px = p.load()
PPT = 3508 / 841.89

col = 300  # blank writing area in every row
runs = []
y = int(190 * PPT)
end = int(730 * PPT)
while y < end:
    if px[int(col * PPT), y] < 100:
        y0 = y
        while y < end and px[int(col * PPT), y] < 100:
            y += 1
        runs.append((y0 / PPT, y / PPT))
    else:
        y += 1

print("=== T4 HORIZONTAL RULES @x=300 (300dpi ink) ===")
rules = []
for a, b in runs:
    th = b - a
    center = (a + b) / 2
    half = 0.75 if th > 1.0 else 0.25
    depth = center + half - 125.95  # whr anchors BOTTOM edge
    kind = "1.5pt" if th > 1.0 else "0.5pt"
    rules.append((center, th, depth, kind))
    print(f"  ink {a:7.2f}..{b:7.2f} thick={th:4.2f} center={center:7.2f} "
          f"whr={depth:7.2f} ({kind})")

pitches = [round(rules[i+1][0] - rules[i][0], 2) for i in range(len(rules)-1)]
print(f"  pitches: {pitches}")

# verticals: left/right borders (span T4 top rule to bottom rule)
def colscan(x0, x1, y):
    cs = [x for x in range(int(x0*PPT), int(x1*PPT)) if px[x, int(y*PPT)] < 100]
    return (cs[0]/PPT, cs[-1]/PPT) if cs else None

def rowscan(x, y0, y1):
    ys = [y for y in range(int(y0*PPT), int(y1*PPT)) if px[int(x*PPT), y] < 100]
    return (ys[0]/PPT, ys[-1]/PPT) if ys else None

print("\n=== T4 VERTICALS ===")
for label, (x0, x1), y in [("left border", (59, 67), 400),
                           ("right border", (528, 536), 400)]:
    r = colscan(x0, x1, y)
    if r:
        c = (r[0] + r[1]) / 2
        ext = rowscan(c, 190, 730)
        print(f"  {label:14s} center={c:.2f} ink extent y={ext[0]:.2f}..{ext[1]:.2f}")

# ---------- 2) label baselines from bbox.html ----------
html = open(BASE + "_inspect/bbox.html").read()
pages = re.findall(r'<page width="[\d.]+" height="[\d.]+">(.*?)</page>', html, re.S)
words = re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', pages[1])

print("\n=== PAGE-2 WORDS (y 140-720) ===")
for x1, y1, x2, y2, t in words:
    x1f, y1f, y2f = float(x1), float(y1), float(y2)
    if 140 < y1f < 720:
        base = y1f + 0.8291 * (y2f - y1f)
        print(f"  base={base:7.2f} depth={base-125.95:7.2f} x={x1f:7.2f} xrel={x1f-63.0:7.2f}  {t}")