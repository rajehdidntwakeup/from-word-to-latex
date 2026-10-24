#!/usr/bin/env python3
"""Settle the -0.45pt text residual: ink-to-ink baseline comparison (ground
truth) + true k-factor derivation for both renderers.

For no-descender words, ink bottom == text baseline. We measure both renders
at 300dpi and derive k = (ink_base - box_yMin) / box_height per renderer."""
import re
import subprocess
from PIL import Image

BASE = "/home/cloude/from-word-to-latex/"
PPT = 3508 / 841.89

# probes: (page, word, x0, y0, x1, y1) — windows avoid all rules/descenders
PROBES = [
    (1, "Bitte", 69.0, 172.0, 127.0, 186.5),
    (1, "BIMK", 188.0, 192.5, 212.0, 206.5),
    (1, "Name", 66.5, 242.0, 96.0, 257.0),
    (1, "PKZ:", 300.0, 242.0, 330.5, 257.0),
    (1, "Datum", 69.0, 315.5, 96.0, 328.5),
    (1, "Unterschrift", 303.5, 315.5, 346.0, 328.5),
    (2, "Nicht-Ziele", 68.0, 402.5, 121.0, 415.5),
    (2, "Zeitplan", 68.0, 601.0, 106.0, 614.5),
]

def ink_bottom(img, x0, y0, x1, y1, thr=128):
    p = Image.open(img).convert("L")
    px = p.load()
    X0, Y0, X1, Y1 = [int(v * PPT) for v in (x0, y0, x1, y1)]
    bot = None
    for y in range(Y0, Y1):
        for x in range(X0, X1):
            if px[x, y] < thr:
                bot = y if bot is None else max(bot, y)
    return bot / PPT if bot else None

def boxes(pdf):
    out = subprocess.run(["pdftotext", "-bbox", pdf, "-"],
                         capture_output=True, text=True, check=True).stdout
    pages = re.findall(r'<page width="[\d.]+" height="[\d.]+">(.*?)</page>', out, re.S)
    res = {}
    for pg, content in enumerate(pages, 1):
        for a, b, c, d, t in re.findall(
                r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>',
                content):
            if (pg, t) not in res:
                res[(pg, t)] = (float(a), float(b), float(c), float(d))
    return res

REF_PDF = BASE + "_inspect/01_Ansuchen Zuteilung wiss Arbeit.pdf"
MY_PDF = BASE + "latex/ansuchen.pdf"
ref_boxes = boxes(REF_PDF)
my_boxes = boxes(MY_PDF)

print(f"{'word':14s} {'ref ink':>8s} {'my ink':>8s} {'ink dy':>7s} | "
      f"{'k_ref':>6s} {'k_mine':>7s}")
k_ref_sum, k_mine_sum, n = 0.0, 0.0, 0
ink_dys = []
for pg, word, x0, y0, x1, y1 in PROBES:
    rb = ref_boxes.get((pg, word))
    mb = my_boxes.get((pg, word))
    if not (rb and mb):
        print(f"{word:14s} box missing: ref={bool(rb)} mine={bool(mb)}")
        continue
    ri = ink_bottom(BASE + f"_inspect/hires-{pg}.png", x0, y0, x1, y1)
    mi = ink_bottom(BASE + f"latex/myhires-{pg}.png", x0, y0, x1, y1)
    if ri is None or mi is None:
        print(f"{word:14s} ink missing: ref={ri} mine={mi}")
        continue
    rh = rb[3] - rb[1]
    mh = mb[3] - mb[1]
    kr = (ri - rb[1]) / rh
    km = (mi - mb[1]) / mh
    dy = mi - ri
    ink_dys.append(dy)
    k_ref_sum += kr
    k_mine_sum += km
    n += 1
    print(f"{word:14s} {ri:8.2f} {mi:8.2f} {dy:+7.2f} | {kr:6.3f} {km:7.3f}")

print()
if n:
    print(f"TRUE ink-to-ink baseline delta: mean {sum(ink_dys)/n:+.2f}pt "
          f"(max |{max(ink_dys, key=abs):+.2f}|)")
    print(f"derived k: ref {k_ref_sum/n:.4f}  mine {k_mine_sum/n:.4f}")
    print(f"qa_diff currently uses: K_REF=0.8291 K_MINE=0.7409")
print("\nVerdict: if ink dy ~ -0.1..0 and k_ref ~0.80, the -0.45 was a")
print("k-model artifact (ref-side); fix K_REF in qa_diff, PDF is correct.")