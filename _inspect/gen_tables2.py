#!/usr/bin/env python3
"""Final generator for T0/T1 table code (Phase 2), all coordinates
precomputed as plain numbers for LaTeX picture \\put (rules keep pt).

Conventions (validated against 300dpi ink + pdftotext):
- pdftotext word box = [baseline - 10.005, baseline + 2.065]  (Tahoma 10pt)
  => baseline = yMin + 10.005
- pen_x = pdftotext xMin - hmtx lsb(first char)
- frame: origin (0,0) = TOP RULE CENTER; x origin = LEFT RULE CENTER (63.0)
  put y anchors are NEGATIVE downward; rules anchored at top edge.
"""
from fontTools.ttLib import TTFont

ASC = 10.005  # Tahoma 10pt hhea ascent

tah = TTFont("/home/cloude/from-word-to-latex/latex/fonts/Tahoma-Regular.ttf")
UPM = tah["head"].unitsPerEm
cmap = tah.getBestCmap()
hmtx = tah["hmtx"]

def lsb(ch):
    return hmtx[cmap[ord(ch)]][1] / UPM * 10

msg = TTFont("/home/cloude/from-word-to-latex/latex/fonts/MSGothic-Regular.ttf")
UPM2 = msg["head"].unitsPerEm
LSB_BOX = msg["hmtx"][msg.getBestCmap()[0x2610]][1] / UPM2 * 10

# ---------- reference pdftotext coordinates (page 1) ----------
YMIN = {"L1": 171.9, "L2": 190.3, "L3": 208.8, "T1r0": 242.0, "T1r1": 314.9}
XMIN = {
    "Bitte wählen:": ("B", 68.6),
    "Bachelorarbeit": ("B", 81.7), "BIMK": ("B", 187.9), "BITI": ("B", 258.7),
    "BSWE": ("B", 329.5), "BWIF": ("B", 400.4),
    "Masterarbeit": ("M", 81.7), "MASE": ("M", 187.9), "MBPM": ("M", 258.7),
    "MCCE": ("M", 329.5), "MDMK": ("M", 400.3), "MEWM": ("M", 471.1),
    "Name der/des Studierenden:": ("N", 68.6), "PKZ:": ("P", 303.1),
    "Datum": ("D", 68.6), "Unterschrift": ("U", 303.1),
}
BOX_XMIN = [68.6, 174.8, 245.6, 316.4, 387.2, 458.0]  # ☐ words, L2 first 5, L3 all 6

# ---------- frame geometry (300dpi ink) ----------
L_RULE_C = 63.0      # left rule center abs
R_RULE_C = 532.06    # right rule center abs
T0_TOP_C = 164.99
T0_BOT_C = 227.51
T1_TOP_C = 241.07
T1_MID_C = 278.27
T1_BOT_C = 333.71
T1_DIV_C = 297.47

W = R_RULE_C - L_RULE_C          # 469.06 rule-center distance
HR_W = W + 1.5                   # horizontal rule width (edge to edge)

def pen(label):
    ch, xm = XMIN[label]
    return xm - lsb(ch)

def rel(x_abs):
    return x_abs - L_RULE_C

# baselines abs
bL1 = YMIN["L1"] + ASC
bL2 = YMIN["L2"] + ASC
bL3 = YMIN["L3"] + ASC
bT1r0 = YMIN["T1r0"] + ASC
bT1r1 = YMIN["T1r1"] + ASC

box_pen = [x - LSB_BOX for x in BOX_XMIN]

lines = []
add = lines.append

def whr(center_depth, thick):
    # anchor y = thick/2 - center (positive = above origin)
    return f"\\whr{{{thick/2 - center_depth:.2f}}}{{{thick:g}}}"

def wvr(x_left, top_anchor, w, h):
    return f"\\wvr{{{x_left:.2f}}}{{{top_anchor:.2f}}}{{{w:g}}}{{{h:.2f}}}"

def wtx(x, base_depth, content):
    return f"\\wtx{{{x:.2f}}}{{{base_depth:.2f}}}{{{content}}}"

# ============ T0 ============
add("% ===== T0: degree-type picker =====")
add("% frame: top rule center at depth 0; left rule center at x=0")
add("\\par\\nointerlineskip\\vspace{6.92pt}\\nointerlineskip")
add("\\begin{wtable}")
add("  " + whr(0, 1.5))
add("  " + whr(T0_BOT_C - T0_TOP_C, 1.5))
# verticals: span from top rule's top edge (-0.75) to bottom rule's bottom edge
vh = (T0_BOT_C - T0_TOP_C) + 1.5
add("  " + wvr(-0.75, 0.75, 1.5, vh))
add("  " + wvr(rel(R_RULE_C) - 0.75, 0.75, 1.5, vh))
# L1
add("  " + wtx(rel(pen("Bitte wählen:")), bL1 - T0_TOP_C, r"\bodystyle Bitte wählen:"))
# L2: boxes 0..4, labels
l2 = ["Bachelorarbeit", "BIMK", "BITI", "BSWE", "BWIF"]
for i, lab in enumerate(l2):
    add("  " + f"\\wcbx{{{rel(box_pen[i]):.2f}}}{{{bL2 - T0_TOP_C:.2f}}}"
        + "  " + wtx(rel(pen(lab)), bL2 - T0_TOP_C, f"\\bodystyle {lab}"))
# L3: boxes 0..5, labels
l3 = ["Masterarbeit", "MASE", "MBPM", "MCCE", "MDMK", "MEWM"]
for i, lab in enumerate(l3):
    add("  " + f"\\wcbx{{{rel(box_pen[i]):.2f}}}{{{bL3 - T0_TOP_C:.2f}}}"
        + "  " + wtx(rel(pen(lab)), bL3 - T0_TOP_C, f"\\bodystyle {lab}"))
add("\\end{wtable}")
add("")

# ============ T1 ============
add("% ===== T1: student data =====")
add("% frame origin = T1 top rule center (76.08pt below T0 origin)")
add("\\par\\nointerlineskip\\vspace{76.08pt}\\nointerlineskip")
add("\\begin{wtable}")
add("  " + whr(0, 1.5))
add("  " + whr(T1_MID_C - T1_TOP_C, 0.5))
add("  " + whr(T1_BOT_C - T1_TOP_C, 1.5))
vh = (T1_BOT_C - T1_TOP_C) + 1.5
add("  " + wvr(-0.75, 0.75, 1.5, vh))
add("  " + wvr(rel(R_RULE_C) - 0.75, 0.75, 1.5, vh))
add("  " + wvr(rel(T1_DIV_C) - 0.25, 0.75, 0.5, vh))
add("  " + wtx(rel(pen("Name der/des Studierenden:")), bT1r0 - T1_TOP_C,
             r"\bodystyle Name der/des Studierenden:"))
add("  " + wtx(rel(pen("PKZ:")), bT1r0 - T1_TOP_C, r"\bodystyle PKZ:"))
add("  " + wtx(rel(pen("Datum")), bT1r1 - T1_TOP_C, r"\bodystyle Datum"))
add("  " + wtx(rel(pen("Unterschrift")), bT1r1 - T1_TOP_C, r"\bodystyle Unterschrift"))
add("\\end{wtable}")

print("\n".join(lines))
print()
print("% sanity: lsb values:", {c: round(lsb(c), 3) for c in "BMNPDU"})
print(f"% ☐ lsb={LSB_BOX:.3f}, pens: Bitte={pen('Bitte wählen:'):.2f}, "
      f"Name={pen('Name der/des Studierenden:'):.2f}, boxes={[round(b,2) for b in box_pen]}")