#!/usr/bin/env python3
"""Locate MY page-1 title baseline + rule positions in the current build."""
from PIL import Image

PPT = 3508 / 841.89

p = Image.open('/home/cloude/from-word-to-latex/latex/myhires-1.png').convert('L')
px = p.load()

def ink(x0, y0, x1, y1, thr=128):
    X0, Y0, X1, Y1 = [int(v * PPT) for v in (x0, y0, x1, y1)]
    b = [None] * 4
    for y in range(Y0, Y1):
        for x in range(X0, X1):
            if px[x, y] < thr:
                b[0] = x if b[0] is None else min(b[0], x)
                b[1] = y if b[1] is None else min(b[1], y)
                b[2] = x if b[2] is None else max(b[2], x)
                b[3] = y if b[3] is None else max(b[3], y)
    return [v / PPT for v in b] if b[0] is not None else None

print("MY current ink:")
b = ink(205, 126, 300, 145)
if b:
    print(f"  title mid-band ink: y={b[1]:.2f}..{b[3]:.2f} => baseline ≈ {b[1]+8.68:.2f} (target 137.81)")
for y in range(int(160*PPT), int(180*PPT)):
    if px[int(300*PPT), y] < 100:
        print(f"  T0 top rule first dark row: y={y/PPT:.2f} (target center 164.99)")
        break
for y in range(int(235*PPT), int(255*PPT)):
    if px[int(300*PPT), y] < 100:
        print(f"  T1 top rule first dark row: y={y/PPT:.2f} (target center 241.07)")
        break