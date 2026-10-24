#!/usr/bin/env python3
"""Baseline-aware coordinate diff between the reference PDF and ours.

Why baseline-aware: `pdftotext -bbox` reports LAYOUT boxes whose vertical
extent comes from each PDF's font-ascent metadata, which DIFFERS between
renderers:
  - LibreOffice reference: Tahoma box = [base - 1.0005em, base + 0.2065em]
  - our XeTeX build:       Tahoma box = [base - 0.718em,  base + 0.251em]
Raw yMin comparison is therefore biased by ~2.8pt at 10pt even when the
baselines match exactly. This tool converts every word box to its text
BASELINE via k-factors (k = ascent / (ascent + descent), empirically
validated against 300dpi ink) and compares baselines + pen origins (xMin).

k-factors (k = ascent / (ascent + descent), derived from 300dpi ink
measurements — see _inspect/k_truth.py; box height varies with each
word's ascender mix, so k is an approximation per renderer):

  Tahoma     reference 0.8291    candidate (XeTeX) 0.7878
  MS Gothic (ballot box, both)    0.8594

Usage:
    python3 qa_diff.py <reference.pdf> <candidate.pdf> [--tol 2.0] [--strict]
"""
import argparse
import re
import subprocess
import sys

WORD_RE = re.compile(
    r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>')
PAGE_RE = re.compile(
    r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', re.S)

K_REF = 0.8291     # Tahoma, LibreOffice reference render
K_MINE = 0.7878    # Tahoma, XeTeX build (derived from 300dpi ink truth)
K_GOTHIC = 0.8594  # MS Gothic ballot box, both renders

BOX = "\u2610"


def baseline(ymin, ymax, is_ref, text):
    h = ymax - ymin
    k = K_GOTHIC if text == BOX else (K_REF if is_ref else K_MINE)
    return ymin + k * h


def parse(pdf, is_ref):
    out = subprocess.run(["pdftotext", "-bbox", pdf, "-"],
                         capture_output=True, text=True, check=True).stdout
    pages = []
    for _w, _h, content in PAGE_RE.findall(out):
        words = []
        for a, b, c, d, e in WORD_RE.findall(content):
            x1, y1, x2, y2 = float(a), float(b), float(c), float(d)
            words.append({
                "x": x1, "y": y1, "x2": x2, "y2": y2, "t": e,
                "base": baseline(y1, y2, is_ref, e),
            })
        pages.append(words)
    return pages


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reference")
    ap.add_argument("candidate")
    ap.add_argument("--tol", type=float, default=2.0,
                    help="tolerance in pt (default 2.0)")
    ap.add_argument("--strict", action="store_true",
                    help="also fail on missing/extra words")
    ap.add_argument("--show", type=int, default=25)
    args = ap.parse_args()

    ref, cand = parse(args.reference, True), parse(args.candidate, False)
    print(f"pages: reference={len(ref)} candidate={len(cand)}")
    if len(ref) != len(cand):
        print("PAGE COUNT MISMATCH ✗")

    all_pairs, missing, extra = [], [], []
    for pi, (rp, cp) in enumerate(zip(ref, cand)):
        unref = list(range(len(rp)))
        for b in cp:
            best, bestd = None, None
            for i in unref:
                a = rp[i]
                if a["t"] != b["t"]:
                    continue
                d = abs(a["x"] - b["x"]) + abs(a["base"] - b["base"])
                if bestd is None or d < bestd:
                    best, bestd = i, d
            if best is None:
                extra.append((pi + 1, b))
            else:
                all_pairs.append((pi + 1, rp[best], b))
                unref.remove(best)
        missing.extend((pi + 1, rp[i]) for i in sorted(unref))

    print(f"paired words: {len(all_pairs)}")
    rows = []
    for pg, a, b in all_pairs:
        dx = b["x"] - a["x"]
        dy = b["base"] - a["base"]
        rows.append((abs(dx) + abs(dy), pg, a["t"], dx, dy))
    rows.sort(reverse=True)

    over = [r for r in rows if abs(r[3]) > args.tol or abs(r[4]) > args.tol]
    print(f"beyond tolerance {args.tol}pt: {len(over)}/{len(rows)}")
    if rows:
        print(f"\nworst {min(args.show, len(rows))} pairs (pen dx / baseline dy, pt):")
        for _s, pg, t, dx, dy in rows[:args.show]:
            flag = " ✗" if abs(dx) > args.tol or abs(dy) > args.tol else ""
            print(f"  p{pg}  {t[:40]:42s} dx={dx:+7.2f} dy={dy:+7.2f}{flag}")

    if missing:
        print(f"\nmissing from candidate ({len(missing)}):")
        for pg, w in missing[:15]:
            print(f"  p{pg}  {w['t'][:50]!r} @ ({w['x']:.1f},{w['base']:.1f})")
        if len(missing) > 15:
            print(f"  ... and {len(missing) - 15} more")
    if extra:
        print(f"\nextra in candidate ({len(extra)}):")
        for pg, w in extra[:15]:
            print(f"  p{pg}  {w['t'][:50]!r} @ ({w['x']:.1f},{w['base']:.1f})")

    fail = bool(over) or (args.strict and (missing or extra))
    print("\nRESULT:", "FAIL ✗" if fail else "PASS ✓")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()