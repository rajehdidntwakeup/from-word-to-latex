#!/usr/bin/env python3
"""Part 3: fonts (embedded), table borders/heights/margins, footer run props,
checkbox run fonts, sectPr details, theme fonts, image info."""
from lxml import etree

BASE = "/home/cloude/from-word-to-latex/_inspect/word/"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

def parse(f):
    return etree.parse(BASE + f)

def tag(node):
    return etree.QName(node).localname

def dump_rpr(rpr, prefix="   "):
    bits = []
    for el in rpr:
        t = tag(el)
        if t == "rFonts":
            bits.append(f"font({el.get(W+'ascii') or el.get(W+'hAnsi') or el.get(W+'cs')})")
        elif t == "sz":
            bits.append(f"{int(el.get(W+'val'))/2}pt")
        elif t == "szCs":
            pass
        elif t in ("b", "i", "u"):
            bits.append(t)
        elif t == "color":
            bits.append(f"#{el.get(W+'val')}")
        elif t == "vertAlign":
            bits.append(f"vertAlign={el.get(W+'val')}")
        elif t == "u":
            bits.append("u")
    return " ".join(bits)

# 1) Embedded fonts
print("===== FONT TABLE =====")
ft = parse("fontTable.xml").getroot()
for f in ft.findall(W + "font"):
    name = f.get(W + "name")
    embedded = f.find(W + "embedRegular")
    sig = f.find(W + "sig")
    charset = f.get(W + "charset") or ""
    print(f"  {name} (charset={charset}) embedded={'YES key='+embedded.get(W+'fontKey') if embedded is not None else 'no'}")

# 2) Theme fonts
print("\n===== THEME FONTS =====")
th = etree.parse(BASE + "theme/theme1.xml").getroot()
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
for scheme in th.findall(".//a:fontScheme/a:majorFont/a:latin", NS) + th.findall(".//a:fontScheme/a:minorFont/a:latin", NS):
    parent_scheme = "major" if "major" in th.findall(".//a:fontScheme/a:majorFont/a:latin", NS) else ""
    print(f"  latin typeface: {scheme.get('typeface')}")
major = th.find(".//a:fontScheme/a:majorFont", NS)
minor = th.find(".//a:fontScheme/a:minorFont", NS)
print(f"  majorFont latin = {major.find('a:latin', NS).get('typeface')}")
print(f"  minorFont latin = {minor.find('a:latin', NS).get('typeface')}")

# 3) Normal style full
print("\n===== NORMAL / STANDARD STYLE =====")
st = parse("styles.xml").getroot()
for s in st.findall(W + "style"):
    if s.get(W + "styleId") in ("Standard", "Normal"):
        print(etree.tostring(s, pretty_print=True).decode()[:1200])

# 4) Table properties per table
print("\n===== TABLE PROPERTIES =====")
doc = parse("document.xml").getroot()
for ti, tbl in enumerate(doc.iter(W + "tbl")):
    tblPr = tbl.find(W + "tblPr")
    print(f"--- TABLE {ti} tblPr ---")
    print("  " + etree.tostring(tblPr, pretty_print=True).decode().replace("\n", "\n  ")[:1500])
    # row heights + cell props of first data rows
    for ri, tr in enumerate(tbl.findall(W + "tr")):
        trPr = tr.find(W + "trPr")
        h = ""
        if trPr is not None:
            trH = trPr.find(W + "trHeight")
            if trH is not None:
                h = f"height={int(trH.get(W+'val'))/567:.2f}cm rule={trH.get(W+'hRule')}"
        print(f"  row {ri}: {h}")

# 5) Footer run props
print("\n===== FOOTER RUN PROPS =====")
ftr = parse("footer1.xml").getroot()
for p in ftr.iter(W + "p"):
    for r in p.findall(W + "r"):
        rpr = r.find(W + "rPr")
        text = "".join(t.text or "" for t in r.findall(W + "t"))
        sym = r.find(W + "sym")
        if text.strip() or sym is not None:
            props = dump_rpr(rpr) if rpr is not None else "(default)"
            print(f"  {text!r:60s} {props}")

# 6) Checkbox run fonts in table 0 cell
print("\n===== TABLE 0 CELL DETAIL (checkbox runs) =====")
for tbl in doc.iter(W + "tbl"):
    grid = tbl.find(W + "tblGrid")
    if grid is not None and len(grid.findall(W + "gridCol")) == 1:
        for p in tbl.iter(W + "p"):
            for r in p.findall(W + "r"):
                rpr = r.find(W + "rPr")
                text = "".join(t.text or "" for t in r.findall(W + "t"))
                if text:
                    props = dump_rpr(rpr) if rpr is not None else "(default)"
                    print(f"  {text!r:55s} {props}")
        break

# 7) sectPr
print("\n===== SECTPR =====")
sect = doc.find(W + "body/" + W + "sectPr")
print(etree.tostring(sect, pretty_print=True).decode()[:2000])