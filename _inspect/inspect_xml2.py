#!/usr/bin/env python3
"""Part 2: header image geometry, footer fields, body element order,
styles defaults, footnotes, checkbox chars, exact spacing values."""
from lxml import etree

BASE = "/home/cloude/from-word-to-latex/_inspect/word/"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"

def parse(f):
    return etree.parse(BASE + f)

def tag(node):
    return etree.QName(node).localname

# 1) HEADER — find drawings (inline or anchor)
print("===== HEADER drawings =====")
hdr = parse("header1.xml").getroot()
for el in hdr.iter():
    if tag(el) in ("inline", "anchor"):
        print(f" {tag(el)}:")
        for sub in el.iter():
            t = tag(sub)
            if t == "ext" and sub.get("cx") and sub.get("cy"):
                print(f"   ext: {int(sub.get('cx'))/360000:.2f} x {int(sub.get('cy'))/360000:.2f} cm")
            elif t == "extent" and sub.get("cx"):
                print(f"   extent: {int(sub.get('cx'))/360000:.2f} x {int(sub.get('cy'))/360000:.2f} cm")
            elif t in ("docPr",):
                print(f"   docPr name={sub.get('name')}")
            elif t == "blip":
                print(f"   blip embed={sub.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')}")
            elif t in ("positionH", "positionV"):
                rel = sub.get("relativeFrom")
                off = sub.find(WP + "posOffset")
                align = sub.find(WP + "align")
                val = (str(int(off.text)/360000) + "cm") if off is not None else (align.text if align is not None else "?")
                print(f"   {t}: relativeFrom={rel} -> {val}")
        # wrap
        for sub in el.iter():
            if tag(sub).startswith("wrap"):
                print(f"   {tag(sub)}")

# 2) FOOTER — fields (PAGE/NUMPAGES)
print("\n===== FOOTER fields =====")
ftr = parse("footer1.xml").getroot()
for p in ftr.iter(W + "p"):
    instrs = [i.text for i in p.iter(W + "instrText")]
    texts = [t.text for t in p.iter(W + "t") if t.text]
    jc = p.find(".//" + W + "jc")
    if instrs or texts:
        print(f"  align={jc.get(W+'val') if jc is not None else None} instr={instrs} text={''.join(texts)!r}")

# 3) BODY element order
print("\n===== BODY element order =====")
doc = parse("document.xml").getroot()
body = doc.find(W + "body")
for i, child in enumerate(body):
    t = tag(child)
    if t == "p":
        texts = "".join(x.text or "" for x in child.iter(W + "t"))
        tabs = len(child.findall(".//" + W + "tab"))
        brs = len(child.findall(".//" + W + "br"))
        spacing = child.find(W + "pPr/" + W + "spacing")
        sp = ""
        if spacing is not None:
            sp = f" spacing({spacing.attrib})"
        print(f"  [{i}] P: {texts[:70]!r}{f' tabs={tabs}' if tabs else ''}{f' br={brs}' if brs else ''}{sp}")
    elif t == "tbl":
        rows = len(child.findall(W + "tr"))
        print(f"  [{i}] TABLE ({rows} rows)")
    else:
        print(f"  [{i}] {t}")

# 4) STYLES defaults
print("\n===== STYLE DEFAULTS =====")
st = parse("styles.xml").getroot()
dd = st.find(W + "docDefaults/" + W + "rPrDefault/" + W + "rPr")
if dd is not None:
    for el in dd.iter():
        t = tag(el)
        if t == "rFonts":
            print(f"  default font: ascii={el.get(W+'ascii')} hAnsi={el.get(W+'hAnsi')} cs={el.get(W+'cs')}")
        elif t == "sz":
            print(f"  default size: {int(el.get(W+'val'))/2}pt")
pd = st.find(W + "docDefaults/" + W + "pPrDefault/" + W + "pPr")
if pd is not None:
    sp = pd.find(W + "spacing")
    if sp is not None:
        print(f"  default para spacing: {sp.attrib}")
norm = None
for s in st.findall(W + "style"):
    if s.get(W + "styleId") == "Standard" or (s.find(W + "name") is not None and s.find(W + "name").get(W + "val") == "Normal"):
        norm = s
        break
if norm is not None:
    print(f"  Normal style XML children: {[tag(c) for c in norm.find(W+'pPr')] if norm.find(W+'pPr') is not None else []}")
    rpr = norm.find(W + "rPr")
    if rpr is not None:
        print(f"  Normal rPr: {[tag(c) for c in rpr]}")

# 5) FOOTNOTES
print("\n===== FOOTNOTES =====")
fn = parse("footnotes.xml").getroot()
for f in fn.findall(W + "footnote"):
    fid = f.get(W + "id")
    texts = "".join(x.text or "" for x in f.iter(W + "t"))
    if texts.strip():
        print(f"  footnote[{fid}]: {texts[:120]!r}")

# 6) CHECKBOX GLYPHS — find w:sym runs in document
print("\n===== SYMBOL RUNS (checkboxes etc.) =====")
doc2 = parse("document.xml").getroot()
for sym in doc2.iter(W + "sym"):
    print(f"  sym: font={sym.get(W+'font')} char={sym.get(W+'char')}")

# 7) ENDNOTES check
en = parse("endnotes.xml").getroot()
print("\nEndnotes with text:", sum(1 for f in en.findall(W+'endnote') if any((x.text or '').strip() for x in f.iter(W+'t'))))

# 8) settings.xml interesting bits
print("\n===== SETTINGS =====")
se = parse("settings.xml").getroot()
for t in ("defaultTabStop", "footnotePr", "evenAndOddHeaders", "titlePg"):
    for el in se.iter(W + t):
        print(f"  {t}: {el.attrib if el.attrib else 'present'}")