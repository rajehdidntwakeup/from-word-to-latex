#!/usr/bin/env python3
"""Detect horizontal table border lines (y positions + thickness) on both
rendered pages, and vertical lines; extract table 0 tcMar; find empty
body paragraph spacing."""
from PIL import Image
from lxml import etree

BASE = "/home/cloude/from-word-to-latex/_inspect/"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

def detect_lines(page_png):
    p = Image.open(page_png).convert("L")
    pw, ph = p.size
    px = p.load()
    ppt = ph / 841.89  # px per pt
    # horizontal lines: rows where a long run (>200px) of dark pixels exists
    hlines = []
    for y in range(ph):
        run = 0; best = 0; start = None; bstart = None
        for x in range(pw):
            if px[x, y] < 160:
                run += 1
                if run > best: best = run; bstart = x - run + 1
            else:
                run = 0
        if best > 250:  # >~180pt long line
            hlines.append((y, bstart, best))
    # merge adjacent y (thick lines)
    merged = []
    for y, x0, ln in hlines:
        if merged and y - merged[-1][0] <= 3:
            merged[-1] = (y, min(merged[-1][1], x0), max(merged[-1][2], ln))
        else:
            merged.append((y, x0, ln))
    return [(round(y/ppt, 1), round(x0/ppt, 1), round(ln/ppt, 1), (y - ([m[0] for m in merged].index(y) if False else 0))) for y, x0, ln in merged], merged

for pg in (1, 2):
    lines_pt, merged = detect_lines(f"{BASE}page-{pg}.png")
    print(f"===== PAGE {pg} horizontal lines (y_pt, x_start_pt, length_pt, thickness_px) =====")
    # thickness: count consecutive dark rows at that y region
    p = Image.open(f"{BASE}page-{pg}.png").convert("L")
    px = p.load()
    pw, ph = p.size
    for y_px, x0, ln in merged:
        # measure thickness at x0+50
        t = 0
        yy = y_px
        while yy < ph and px[x0 + 60, yy] < 160:
            t += 1; yy += 1
        print(f"  y={y_px/ph*841.89:7.1f}pt x0={x0/pw*595.3:6.1f} len={ln/pw*595.3:6.1f} thick={t}px ({t/1.389:.2f}pt)")

# vertical lines page 1
p = Image.open(f"{BASE}page-1.png").convert("L")
pw, ph = p.size
px = p.load()
vlines = []
for x in range(pw):
    run = 0; best = 0
    for y in range(ph):
        if px[x, y] < 160: run += 1; best = max(best, run)
        else: run = 0
    if best > 40:
        vlines.append((x, best))
merged_v = []
for x, ln in vlines:
    if merged_v and x - merged_v[-1][0] <= 3:
        merged_v[-1] = (x, max(merged_v[-1][1], ln))
    else:
        merged_v.append((x, ln))
print("===== PAGE 1 vertical lines (x_pt, max_run_px) =====")
for x, ln in merged_v:
    print(f"  x={x/pw*595.3:6.1f}pt run={ln}px ({ln/1.389:.0f}pt)")

# table 0 tcMar detail
doc = etree.parse(BASE + "word/document.xml").getroot()
tbl0 = list(doc.iter(W + "tbl"))[0]
tcPr = tbl0.find(".//" + W + "tcPr")
print("\n===== TABLE 0 first tcPr =====")
print(etree.tostring(tcPr, pretty_print=True).decode()[:800].replace('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" ', ""))