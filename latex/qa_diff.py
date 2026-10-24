#!/usr/bin/env python3
"""Word-level coordinate diff between the reference PDF and the LaTeX output.

Usage:
    python3 qa_diff.py <reference.pdf> <candidate.pdf> [--tol 2.0] [--strict]

Parses `pdftotext -bbox` output of both PDFs, pairs words by text content
(nearest position), and reports positional deltas. Missing/extra words are
listed but only fail with --strict (use it once Phases 2-4 add all text).
"""
import argparse
import re
import subprocess
import sys

WORD_RE = re.compile(
    r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>')
PAGE_RE = re.compile(
    r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', re.S)


def parse(pdf):
    out = subprocess.run(["pdftotext", "-bbox", pdf, "-"],
                         capture_output=True, text=True, check=True).stdout
    pages = []
    for _w, _h, content in PAGE_RE.findall(out):
        words = [{"x": float(a), "y": float(b), "x2": float(c),
                  "y2": float(d), "t": e}
                 for a, b, c, d, e in WORD_RE.findall(content)]
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
    ap.add_argument("--show", type=int, default=25,
                    help="how many worst pairs to print (default 25)")
    args = ap.parse_args()

    ref, cand = parse(args.reference), parse(args.candidate)
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
                d = abs(a["x"] - b["x"]) + abs(a["y"] - b["y"])
                if bestd is None or d < bestd:
                    best, bestd = i, d
            if best is None:
                extra.append((pi + 1, b))
            else:
                a = rp[best]
                unref.remove(best)
                all_pairs.append((pi + 1, a, b))
        missing.extend((pi + 1, rp[i]) for i in sorted(unref))

    print(f"paired words: {len(all_pairs)}")
    rows = []
    for pg, a, b in all_pairs:
        dx, dy = b["x"] - a["x"], b["y"] - a["y"]
        rows.append((abs(dx) + abs(dy), pg, a["t"], dx, dy))
    rows.sort(reverse=True)

    over = [r for r in rows if abs(r[3]) > args.tol or abs(r[4]) > args.tol]
    print(f"beyond tolerance {args.tol}pt: {len(over)}/{len(rows)}")
    if rows:
        print(f"\nworst {min(args.show, len(rows))} pairs (Δx/Δy in pt):")
        for _s, pg, t, dx, dy in rows[:args.show]:
            flag = " ✗" if abs(dx) > args.tol or abs(dy) > args.tol else ""
            print(f"  p{pg}  {t[:40]:42s} dx={dx:+7.2f} dy={dy:+7.2f}{flag}")

    if missing:
        print(f"\nmissing from candidate ({len(missing)}):")
        for pg, w in missing[:15]:
            print(f"  p{pg}  {w['t'][:50]!r} @ ({w['x']:.1f},{w['y']:.1f})")
        if len(missing) > 15:
            print(f"  ... and {len(missing) - 15} more")
    if extra:
        print(f"\nextra in candidate ({len(extra)}):")
        for pg, w in extra[:15]:
            print(f"  p{pg}  {w['t'][:50]!r} @ ({w['x']:.1f},{w['y']:.1f})")

    fail = bool(over) or (args.strict and (missing or extra))
    print("\nRESULT:", "FAIL ✗" if fail else "PASS ✓")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()