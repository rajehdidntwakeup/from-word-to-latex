#!/usr/bin/env python3
"""Phase 3 extraction: exact T2/T3 coordinates for the LaTeX build.
1) Word baselines (vector-exact, from pdftotext -bbox of the reference)
2) Superscript '1' metrics (size, baseline)
3) Rule spans at 300dpi (T2 top/mid/bottom, T3 top/r0r1/r1r2/bottom)
4) T3 vertical dividers (x centers, extents)
Outputs LaTeX-ready numbers (depths rel. Word top 125.95pt, x rel. 63pt)."""
import re
from PIL import Image

BASE = "/home/cloude/from-word-to-latex/"

# ---------- 1) words from bbox.html (vector-exact) ----------
html = open(BASE + "_inspect/bbox.html").read()
pages = re.findall(r'<page width="[\d.]+" height="[\d.]+">(.*?)</page>', html, re.S)
words = re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', pages[0])

def kref(text):
    return 0.8594 if text == "\u2610" else 0.8291

rows = []
for x1, y1, x2, y2, t in words:
    x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
    if 340 < y1 < 776:
        base = y1 + kref(t) * (y2 - y1)
        rows.append((base, x1, y1, y2, t))
rows.sort()

lines = []
for r in rows:
    if lines and abs(r[0] - lines[-1][0][0]) < 3:
        lines[-1].append(r)
    else:
        lines.append([r])

print("=== T2/T3 LINES ===")
for ln in lines:
    base = ln[0][0]
    ws = "  ".join(f"{t}@{x:.2f}" for _, x, _, _, t in sorted(ln, key=lambda r: r[1]))
    print(f"base={base:7.2f} depth={base-125.95:7.2f}: {ws}")

print("\n=== SUPERSCRIPT '1' ===")
for base, x, y1, y2, t in rows:
    if t == "1":
        h = y2 - y1
        print(f"  xMin={x:.2f} yMin={y1:.2f} h={h:.2f} size={h/1.2071:.2f} base={base:.2f} "
              f"depth={base-125.95:.2f} xcall={x-63.0:.2f}")

# ---------- 3) rules at 300dpi ----------
p = Image.open(BASE + "_inspect/hires-1.png").convert("L")
px = p.load()
PPT = 3508 / 841.89

col = 300
runs = []
y = int(340 * PPT)
end = int(790 * PPT)
while y < end:
    if px[int(col * PPT), y] < 100:
        y0 = y
        while y < end and px[int(col * PPT), y] < 100:
            y += 1
        runs.append((y0 / PPT, y / PPT))
    else:
        y += 1

print("\n=== HORIZONTAL RULES @x=300 (300dpi ink) ===")
for a, b in runs:
    c = (a + b) / 2
    th = b - a
    half = 0.75 if th > 1.0 else 0.25
    print(f"  top={a:7.2f} bot={b:7.2f} thick={th:4.2f} center={c:7.2f} "
          f"whr_depth={c+half-125.95:7.2f}")

# ---------- 4) T3 verticals ----------
def colscan(x0, x1, y):
    cols = [x for x in range(int(x0*PPT), int(x1*PPT)) if px[x, int(y*PPT)] < 100]
    return (cols[0]/PPT, cols[-1]/PPT) if cols else None

def rowscan(x, y0, y1):
    ys = [y for y in range(int(y0*PPT), int(y1*PPT)) if px[int(x*PPT), y] < 100]
    return (ys[0]/PPT, ys[-1]/PPT) if ys else None

print("\n=== T3 VERTICALS (300dpi ink) ===")
for label, (x0, x1), y in [("div1 @r1", (198, 212), 707),
                           ("div2 @r1", (291, 304), 707),
                           ("div2 @r2", (291, 304), 750),
                           ("left border @T2", (59, 67), 500),
                           ("right border @T2", (528, 536), 500),
                           ("ANY vertical @r0 (203..206)", (200, 208), 690)]:
    r = colscan(x0, x1, y)
    if r:
        c = (r[0] + r[1]) / 2
        print(f"  {label:28s} span={r[0]:.2f}..{r[1]:.2f} center={c:.2f} xcall_left={r[0]-63.0:.2f}")
    else:
        print(f"  {label:28s} NONE")

print("\n=== DIVIDER EXTENTS ===")
d1 = colscan(198, 212, 707)
if d1:
    c1 = (d1[0] + d1[1]) / 2
    ext = rowscan(c1, 690, 726)
    print(f"  div1 center x={c1:.2f} ink extent y={ext[0]:.2f}..{ext[1]:.2f}")
d2 = colscan(291, 304, 750)
if d2:
    c2 = (d2[0] + d2[1]) / 2
    ext = rowscan(c2, 690, 771)  # stop before the bottom rule merges the run
    print(f"  div2 center x={c2:.2f} ink extent y={ext[0]:.2f}..{ext[1]:.2f} (bottom rule top ~772)")