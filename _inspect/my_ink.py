#!/usr/bin/env python3
"""Diff MY render vs reference ink at key glyphs (T0/T1)."""
from PIL import Image

p = Image.open('/home/cloude/from-word-to-latex/latex/myhires-1.png').convert('L')
pw, ph = p.size
px = p.load()
PPT = ph / 841.89

def ink(x0, y0, x1, y1, thr=128):
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

print("MY renders (300dpi):")
for label, (x0, y0, x1, y1) in {
    "☐ first L2": (66, 190, 82, 208),
    "BIMK": (185, 190, 213, 208),
    "Bachelorarbeit": (78, 190, 148, 208),
    "Name der/des": (64, 238, 178, 258),
    "Datum": (64, 312, 96, 330),
    "Unterschrift": (300, 312, 346, 330),
}.items():
    b = ink(x0, y0, x1, y1)
    if b:
        print(f"  {label:15s} ink x={b[0]:.2f}..{b[2]:.2f} y={b[1]:.2f}..{b[3]:.2f}")

print("\nREFERENCE (earlier 300dpi):")
print("  ☐ ink x=69.84..77.04 y=192.71..199.91")
print("  BIMK x=188.63..210.95 y=192.95..199.91")
print("  Bachelorarbeit x=82.56..144.47 y=192.47..200.15")
print("  Name der/des x=66.00..174.71 y=240.47..253.19 baseline=253.19")
print("  Datum x=69.36..94.56 y=317.51..324.71 baseline=324.71")
print("  Unterschrift x=303.83..344.63 y=317.03..324.71 baseline=324.71")