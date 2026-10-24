#!/usr/bin/env python3
"""Part 4: tblPr children (no namespaces), sectPr, table 4 cell paragraphs,
checkbox codepoints, image dims."""
from lxml import etree
from PIL import Image

BASE = "/home/cloude/from-word-to-latex/_inspect/word/"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

def parse(f):
    return etree.parse(BASE + f)

def tag(node):
    return etree.QName(node).localname

def clean(el, depth=0):
    """Serialize element ignoring namespaces, compact."""
    out = []
    attrs = {k.split("}")[-1]: v for k, v in el.attrib.items()}
    out.append("  " * depth + f"<{tag(el)} {attrs}>")
    for c in el:
        out.extend(clean(c, depth + 1))
    return out

# 1) tblPr children per table
doc = parse("document.xml").getroot()
tables = list(doc.iter(W + "tbl"))
for ti, tbl in enumerate(tables):
    print(f"===== TABLE {ti} tblPr =====")
    tblPr = tbl.find(W + "tblPr")
    if tblPr is not None:
        print("\n".join(clean(tblPr)))
    # grid
    grid = tbl.find(W + "tblGrid")
    if grid is not None:
        print("  grid:", [round(int(g.get(W + "w")) / 567, 2) for g in grid.findall(W + "gridCol")])
    # first row cell margins / borders from tcPr of first cell
    tr0 = tbl.find(W + "tr")
    if tr0 is not None:
        tcPr = tr0.find(W + "tc/" + W + "tcPr")
        if tcPr is not None:
            print("  -- first cell tcPr --")
            print("\n".join(clean(tcPr, 1)))
    # row heights
    for ri, tr in enumerate(tbl.findall(W + "tr")):
        trPr = tr.find(W + "trPr")
        if trPr is not None:
            print(f"  -- row {ri} trPr --")
            print("\n".join(clean(trPr, 1)))
    print()

# 2) sectPr clean
print("===== SECTPR =====")
sect = doc.find(W + "body/" + W + "sectPr")
print("\n".join(clean(sect)))

# 3) table 4 cell paragraphs (how height is created)
print("\n===== TABLE 4 ROW CELLS: paragraph counts =====")
t4 = tables[4]
for ri, tr in enumerate(t4.findall(W + "tr")):
    for tc in tr.findall(W + "tc"):
        paras = tc.findall(W + "p")
        texts = []
        for p in paras:
            t = "".join(x.text or "" for x in p.iter(W + "t"))
            # count empty runs/breaks
            texts.append(t[:40] if t.strip() else "(empty)")
        n_nonempty = sum(1 for t in texts if t != "(empty)")
        print(f" row {ri}: {len(paras)} paras, nonempty={n_nonempty}, first={texts[0]!r}, sample={texts[:3]}")

# 4) checkbox codepoints in whole document
print("\n===== SPECIAL CHARACTERS (non-ASCII) =====")
seen = {}
for t in doc.iter(W + "t"):
    if t.text:
        for ch in t.text:
            if ord(ch) > 127:
                seen.setdefault(f"U+{ord(ch):04X} {ch!r}", 0)
                seen[f"U+{ord(ch):04X} {ch!r}"] += 1
for k, v in sorted(seen.items()):
    print(f"  {k}: x{v}")
# also sym elements anywhere (header/footer too)
for fname in ("document.xml", "header1.xml", "footer1.xml"):
    root = parse(fname).getroot()
    for sym in root.iter(W + "sym"):
        print(f"  SYM in {fname}: font={sym.get(W+'font')} char={sym.get(W+'char')}")

# 5) image dims
print("\n===== MEDIA =====")
for f in ("image1.png",):
    im = Image.open(BASE + "media/" + f)
    print(f"  image1.png: {im.size} px, mode={im.mode}, dpi={im.info.get('dpi')}")
with open(BASE + "media/image2.svg") as fh:
    svg = fh.read(400)
print(f"  image2.svg head: {svg[:200]!r}")