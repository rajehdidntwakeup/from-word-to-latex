#!/usr/bin/env python3
"""Precise ink measurements from the 300dpi reference render (hires-1.png).
Resolves: exact rule x-positions, text pen origins (via font LSBs), the
checkbox glyph baseline, and T0/T1 line baselines."""
from PIL import Image
from fontTools.ttLib import TTFont

BASE = "/home/cloude/from-word-to-latex/_inspect/"
p = Image.open(BASE + "hires-1.png").convert("L")
pw, ph = p.size
px = p.load()
PPT = ph / 841.89  # px per pt (~4.1667)

def ink_bbox(x0, y0, x1, y1, thr=128):
    """ink bbox in PT within the given pt-rect."""
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

def vline_center(x0, x1, y):
    """center x of a dark vertical line at given y (pt), searching x range."""
    X0, X1, Y = int(x0 * PPT), int(x1 * PPT), int(y * PPT)
    cols = [x for x in range(X0, X1) if px[x, Y] < 128]
    return (min(cols) + max(cols)) / 2 / PPT if cols else None

def hline_span(y0, y1, x):
    """vertical span of a dark horizontal rule at given x (pt)."""
    Y0, Y1, X = int(y0 * PPT), int(y1 * PPT), int(x * PPT)
    rows = [y for y in range(Y0, Y1) if px[X, y] < 128]
    return (min(rows) / PPT, max(rows) / PPT) if rows else None

print(f"render {pw}x{ph}px, {PPT:.4f} px/pt")

# --- 1) rule positions in T1 area (y=250..330) ---
left_c = vline_center(58, 68, 300)
right_c = vline_center(525, 540, 300)
div_c = vline_center(292, 302, 250)
print(f"T1 left rule center:  {left_c:.2f}pt")
print(f"T1 divider center:    {div_c:.2f}pt")
print(f"T1 right rule center: {right_c:.2f}pt")

# --- 2) rule y spans at x=200 ---
for name, yguess in [("T0 top", 165.3), ("T0 bottom", 227.9), ("T1 top", 241.6),
                     ("T1 mid", 278.3), ("T1 bottom", 334.4)]:
    span = hline_span(yguess - 3, yguess + 3, 200)
    print(f"{name} rule span: {span[0]:.2f} .. {span[1]:.2f}pt (h={span[1]-span[0]:.2f})")

# --- 3) text ink: Name / PKZ / Datum ---
tah = TTFont("/home/cloude/from-word-to-latex/latex/fonts/Tahoma-Regular.ttf")
upm = tah["head"].unitsPerEm
gs = tah.getGlyphSet()
cmap = tah.getBestCmap()
def lsb(ch):
    g = tah.getGlyphOrder()[cmap[ord(ch)]] if False else cmap[ord(ch)]
    return tah["hmtx"][g][0] / upm * 10

for label, (x0, y0, x1, y1, first_char) in {
    "Name der/des Studierenden:": (66, 240, 175, 256, "N"),
    "PKZ:": (300, 240, 330, 256, "P"),
    "Datum (T1 r1)": (66, 312, 95, 330, "D"),
    "Unterschrift": (300, 312, 345, 330, "U"),
    "Bitte wählen: (T0)": (66, 169, 130, 186, "B"),
    "BIMK": (186, 189, 213, 205, "B"),
    "Bachelorarbeit": (80, 189, 147, 205, "B"),
}.items():
    b = ink_bbox(x0, y0, x1, y1)
    if b:
        pen_x = b[0] - lsb(first_char)
        print(f"{label:30s} ink x={b[0]:.2f}..{b[2]:.2f} y={b[1]:.2f}..{b[3]:.2f}"
              f"  -> pen_x={pen_x:.2f} baseline={b[3]:.2f}")

# --- 4) checkbox ink in T0 line 2 (first box) ---
b = ink_bbox(66, 189, 80, 204)
print(f"☐ ink bbox: x={b[0]:.2f}..{b[2]:.2f} y={b[1]:.2f}..{b[3]:.2f}")

# MS Gothic ☐ glyph bounds
mg = TTFont("/home/cloude/from-word-to-latex/latex/fonts/MSGothic-Regular.ttf")
upm2 = mg["head"].unitsPerEm
gname = mg.getBestCmap()[0x2610]
glyf = mg["glyf"][gname]
print(f"MSGothic ☐ glyf bounds: x {glyf.xMin}..{glyf.xMax}, y {glyf.yMin}..{glyf.yMax} (upm {upm2})")
print(f"  -> ink at 10pt: x {(glyf.xMin)/upm2*10:.2f}..{glyf.xMax/upm2*10:.2f}, "
      f"y {(glyf.yMin)/upm2*10:.2f}..{glyf.yMax/upm2*10:.2f} rel. baseline; advance {mg['hmtx'][gname][0]/upm2*10:.2f}")
# baseline position from ink: baseline = ink_bottom - (-yMin)/upm*10
base = b[3] - (-glyf.yMin) / upm2 * 10
print(f"  -> ☐ glyph baseline from ink: {base:.2f}pt abs")
print(f"  -> ☐ glyph ORIGIN (pen) from ink left: {b[0] - glyf.xMin/upm2*10:.2f}pt abs")