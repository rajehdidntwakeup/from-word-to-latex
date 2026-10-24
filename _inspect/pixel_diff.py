#!/usr/bin/env python3
"""Pixel-level diff of the T0/T1 region (page 1 top half) + full page stats.
150dpi renders, tolerance-tolerant diff (blur 2px to ignore antialiasing)."""
from PIL import Image, ImageChops, ImageFilter

SCALE = 150 / 72  # dpi per pt

def load(img):
    return Image.open(img).convert("L")

ref = load("/home/cloude/from-word-to-latex/_inspect/page-1.png")  # 100dpi
mine = load("/home/cloude/from-word-to-latex/latex/mine-1.png")    # 100dpi
print(f"ref size {ref.size}, mine {mine.size}")
if ref.size != mine.size:
    mine = mine.resize(ref.size)

# region: y 160..340pt (T0+T1), x 60..535pt at 100dpi (px = pt*100/72)
x0, y0, x1, y1 = int(60*100/72), int(160*100/72), int(535*100/72), int(340*100/72)
r = ref.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(1))
m = mine.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(1))

diff = ImageChops.difference(r, m)
bbox = diff.getbbox()
hist = diff.histogram()
total = sum(hist)
sig = sum(hist[40:])  # pixels differing by >40/255
print(f"T0+T1 region: {r.size[0]}x{r.size[1]} px, differing>40: {sig} ({100*sig/ (r.size[0]*r.size[1]):.2f}%)")

# full page (informative; T2/T3/T4 regions will differ by design)
rd = ImageChops.difference(ref.filter(ImageFilter.GaussianBlur(1)), mine.filter(ImageFilter.GaussianBlur(1)))
hs = rd.histogram()
sig_full = sum(hs[40:])
print(f"full page 1: differing>40: {sig_full} ({100*sig_full/(ref.size[0]*ref.size[1]):.2f}%) [T2/T3/T4 still TODO]")

# page 2
ref2 = load("/home/cloude/from-word-to-latex/_inspect/page-2.png")
mine2 = load("/home/cloude/from-word-to-latex/latex/mine-2.png")
if ref2.size != mine2.size:
    mine2 = mine2.resize(ref2.size)
rd2 = ImageChops.difference(ref2.filter(ImageFilter.GaussianBlur(1)), mine2.filter(ImageFilter.GaussianBlur(1)))
hs2 = rd2.histogram()
sig2 = sum(hs2[40:])
print(f"full page 2: differing>40: {sig2} ({100*sig2/(ref2.size[0]*ref2.size[1]):.2f}%) [T4 still TODO]")