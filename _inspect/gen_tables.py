#!/usr/bin/env python3
"""Generate the exact-coordinate picture code for tables T0 and T1 (and later
T2/T3/T4) from the measured reference geometry. All arithmetic precomputed,
because LaTeX picture \\put coords must be plain numbers.

Outputs .tex fragments to stdout; paste-ready for ansuchen.tex."""

# ---- shared frame geometry (measured, PLAN.md §2-3) ----
TEXT_W = 472.06          # total frame width incl. both 1.5pt rules
HALF = 0.75              # half of 1.5pt rule

def thr(bottom_depth, thick):
    """thick horizontal rule; bottom_depth = depth of rule's BOTTOM edge"""
    return f"\\wthr{{{bottom_depth:g}}}{{{thick:g}}}"

def tnr(bottom_depth):
    return f"\\wtnr{{{bottom_depth:g}}}"

def tvr(x_left, top_depth, height, thick):
    """vertical rule; x_left = left edge, top_depth = depth of TOP edge"""
    return f"\\wtvr{{{x_left:g}}}{{{top_depth:g}}}{{{height:g}}}{{{thick:g}}}"

def txt(x, base_depth, content):
    return f"\\wtt{{{x:g}}}{{{base_depth:g}}}{{{content}}}"

def cbx(x, label_base_depth, extra=0.75):
    """checkbox glyph; its baseline sits 0.75pt below the label baseline"""
    return f"\\wtcbx{{{x:g}}}{{{label_base_depth + extra:g}}}"


# ================= T0: degree picker =================
# frame: top rule top=0, bottom rule spans 62.6..64.1 (bottom edge 64.1)
# baselines (depth from frame top): 19.16 / 37.51 / 56.01
t0 = []
t0.append("% ===== T0: degree-type picker =====")
t0.append("\\par\\nointerlineskip\\vspace{9.75pt}\\nointerlineskip")
t0.append("\\begin{wtable}")
t0.append("  " + thr(1.5, 1.5) + "                     % top rule")
t0.append("  " + thr(64.1, 1.5) + "                   % bottom rule")
t0.append("  " + tvr(-HALF, 0, 64.1 + HALF, 1.5) + "         % left border")
t0.append("  " + tvr(470.56, 0, 64.1 + HALF, 1.5) + "    % right border")
b1, b2, b3 = 19.16, 37.51, 56.01
t0.append("  " + txt(6.24, b1, r"\bodystyle Bitte wählen:"))
line2 = [(6.24, "Bachelorarbeit"), (112.44, "BIMK"), (183.24, "BITI"),
         (254.04, "BSWE"), (324.84, "BWIF")]
line3 = [(6.24, "Masterarbeit"), (112.44, "MASE"), (183.24, "MBPM"),
         (254.04, "MCCE"), (324.84, "MDMK"), (395.64, "MEWM")]
# labels start 13.1pt after box x-origin
for i, (x, label) in enumerate(line2):
    cmd = cbx(x, b2) + "  " + txt(x + 13.1, b2, f"\\bodystyle {label}")
    t0.append("  " + cmd + ("" if i else "  % line 2"))
for i, (x, label) in enumerate(line3):
    cmd = cbx(x, b3) + "  " + txt(x + 13.1, b3, f"\\bodystyle {label}")
    t0.append("  " + cmd + ("" if i else "  % line 3"))
t0.append("\\end{wtable}")
t0.append("")

# ================= T1: student data =================
# frame top=0; rules: top 0..1.5, mid 36.7..37.2, bottom 92.8..94.3
# baselines: r0 12.91, r1 85.81; divider boundary x=234.94 (0.5pt rule)
t1 = []
t1.append("% ===== T1: student data =====")
t1.append("\\par\\nointerlineskip\\vspace{76.3pt}\\nointerlineskip")
t1.append("\\begin{wtable}")
t1.append("  " + thr(1.5, 1.5))
t1.append("  " + tnr(37.2) + "                          % mid rule")
t1.append("  " + thr(94.3, 1.5) + "                   % bottom rule")
t1.append("  " + tvr(-HALF, 0, 94.3 + HALF, 1.5) + "         % left border")
t1.append("  " + tvr(470.56, 0, 94.3 + HALF, 1.5) + "    % right border")
t1.append("  " + tvr(234.94, 0, 94.3 + HALF, 0.5) + "     % column divider")
t1.append("  " + txt(6.24, 12.91, r"\bodystyle Name der/des Studierenden:"))
t1.append("  " + txt(240.79, 12.91, r"\bodystyle PKZ:"))
t1.append("  " + txt(6.24, 85.81, r"\bodystyle Datum"))
t1.append("  " + txt(240.79, 85.81, r"\bodystyle Unterschrift"))
t1.append("\\end{wtable}")

print("\n".join(t0))
print()
print("\n".join(t1))