#!/usr/bin/env python3
"""Extract readable text + key formatting from header/footer/document XML,
plus image geometry, tab stops, and cell properties."""
import re, sys
from lxml import etree

BASE = "/home/cloude/from-word-to-latex/_inspect/word/"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
PIC = "{http://schemas.openxmlformats.org/drawingml/2006/picture}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"

def parse(fname):
    return etree.parse(BASE + fname)

def para_text(p):
    parts = []
    for node in p.iter():
        tag = etree.QName(node).localname
        if tag == "t":
            parts.append(node.text or "")
        elif tag == "tab":
            parts.append("\t")
        elif tag == "br" and node.getparent().tag.endswith("}p"):
            pass
        elif tag == "ptab" or tag == "tab":
            parts.append("\t")
        elif tag in ("noBreakHyphen",):
            parts.append("-")
        elif tag == "sym":
            parts.append(f"[SYM {node.get(W+'char')}]")
    # note: field codes (fldChar/instrText) excluded deliberately
    return "".join(parts)

def dump_paragraphs(root, label):
    print(f"########## {label} ##########")
    for p in root.iter(W + "p"):
        tabs = p.findall(".//" + W + "tabs/" + W + "tab")
        ptab_info = []
        for t in p.findall(".//" + W + "ptab"):
            ptab_info.append(f"ptab@{t.get(W+'alignment')}")
        jc = p.find(".//" + W + "pPr/" + W + "jc")
        align = jc.get(W + "val") if jc is not None else None
        # images
        imgs = []
        for inline in p.iter(WP + "inline"):
            ext = inline.find(".//" + A + "ext")
            w_emu = int(ext.get("cx")); h_emu = int(ext.get("cy"))
            docpr = inline.find(WP + "docPr")
            imgs.append({
                "name": docpr.get("name") if docpr is not None else "?",
                "cm": (round(w_emu/360000, 2), round(h_emu/360000, 2)),
            })
        txt = para_text(p)
        if txt.strip() or imgs:
            extras = []
            if align: extras.append(f"align={align}")
            if tabs: extras.append(f"tabs={len(tabs)}")
            if ptab_info: extras.append(",".join(ptab_info))
            if imgs: extras.append(f"IMG {imgs}")
            print(f"  [{label}] align={align} :: {repr(txt)}  {extras if extras else ''}")
    print()

dump_paragraphs(parse("header1.xml").getroot(), "HEADER")
dump_paragraphs(parse("footer1.xml").getroot(), "FOOTER")

# --- document.xml: tables in detail ---
doc = parse("document.xml").getroot()
print("########## DOCUMENT TABLES (cell-by-cell with merged cells) ##########")
for ti, tbl in enumerate(doc.iter(W + "tbl")):
    print(f"--- TABLE {ti} ---")
    # grid columns
    grid = tbl.find(W + "tblGrid")
    if grid is not None:
        cols = [round(int(gc.get(W+"w"))/567, 2) for gc in grid.findall(W + "gridCol")]
        print(f"  gridCols(cm): {cols}")
    for ri, tr in enumerate(tbl.findall(W + "tr")):
        cells = []
        for tc in tr.findall(W + "tc"):
            tcPr = tc.find(W + "tcPr")
            merge = ""
            if tcPr is not None:
                vm = tcPr.find(W + "vMerge")
                if vm is not None:
                    merge = f"[vM:{vm.get(W+'val') or 'cont'}]"
                gs = tcPr.find(W + "gridSpan")
                if gs is not None:
                    merge += f"[span:{gs.get(W+'val')}]"
            text = " | ".join(para_text(p) for p in tc.findall(W + "p"))
            cells.append(f"{merge}{'{'}{text.strip()[:80]}{'}'}")
        print(f"  r{ri}: {cells}")
    print()