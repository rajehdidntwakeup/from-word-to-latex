#!/usr/bin/env python3
"""Part 5: header rels + anchor, table cell run formatting, footnote superscript."""
from lxml import etree

BASE = "/home/cloude/from-word-to-latex/_inspect/word/"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"

def parse(f):
    return etree.parse(BASE + f)

def tag(node):
    return etree.QName(node).localname

def runinfo(r):
    rpr = r.find(W + "rPr")
    bits = []
    if rpr is not None:
        for el in rpr:
            t = tag(el)
            if t == "rFonts":
                f = el.get(W + "ascii") or el.get(W + "hAnsi") or el.get(W + "cs") or el.get(W + "asciiTheme") or ""
                bits.append(f"font={f}")
            elif t == "sz":
                bits.append(f"{int(el.get(W+'val'))/2:g}pt")
            elif t == "b":
                bits.append("b")
            elif t == "i":
                bits.append("i")
            elif t == "u":
                bits.append("u")
            elif t == "vertAlign":
                bits.append(f"vert={el.get(W+'val')}")
    text = "".join(t.text or "" for t in r.findall(W + "t"))
    tabs = len(r.findall(W + "tab"))
    sym = r.find(W + "sym")
    if sym is not None:
        bits.append(f"SYM:{sym.get(W+'font')}:{sym.get(W+'char')}")
    ft = r.find(".//" + W + "footnoteReference")
    if ft is not None:
        bits.append(f"FOOTNOTE_REF id={ft.get(W+'id')}")
    if text or tabs:
        bits.append(repr(text if text else ("<TAB>" * tabs)))
    return " ".join(bits)

def dump_cell_paras(tbl, label, max_rows=None, max_paras=None):
    print(f"##### {label} #####")
    rows = tbl.findall(W + "tr")
    for ri, tr in enumerate(rows):
        if max_rows and ri >= max_rows: break
        for ci, tc in enumerate(tr.findall(W + "tc")):
            # gridSpan
            tcPr = tc.find(W + "tcPr")
            span = ""
            if tcPr is not None:
                gs = tcPr.find(W + "gridSpan")
                if gs is not None:
                    span = f" (span {gs.get(W+'val')})"
                vm = tcPr.find(W + "vMerge")
                if vm is not None:
                    span += f" (vMerge {vm.get(W+'val') or 'cont'})"
            print(f"--- row{ri} cell{ci}{span} ---")
            paras = tc.findall(W + "p")
            for pi, p in enumerate(paras):
                if max_paras and pi >= max_paras: 
                    print(f"    ... {len(paras)-max_paras} more paras")
                    break
                ppr = p.find(W + "pPr")
                pinfo = []
                if ppr is not None:
                    for el in ppr:
                        t = tag(el)
                        if t == "tabs":
                            stops = [{k.split('}')[-1]: v for k, v in s.attrib.items()} for s in el]
                            pinfo.append(f"tabs={stops}")
                        elif t == "jc":
                            pinfo.append(f"align={el.get(W+'val')}")
                        elif t == "spacing":
                            pinfo.append(f"spacing={ {k.split('}')[-1]: v for k, v in el.attrib.items()} }")
                        elif t == "ind":
                            pinfo.append(f"ind={ {k.split('}')[-1]: int(v)/567 for k, v in el.attrib.items() if v} }")
                print(f"  p{pi}: {' '.join(pinfo) if pinfo else '(no pPr)'}")
                for r in p.findall(W + "r"):
                    info = runinfo(r)
                    if info:
                        print(f"     run: {info}")
    print()

doc = parse("document.xml").getroot()
tables = list(doc.iter(W + "tbl"))

dump_cell_paras(tables[0], "TABLE 0 (Artenwahl)")
dump_cell_paras(tables[1], "TABLE 1 (Name/PKZ/Datum/Unterschrift)")
dump_cell_paras(tables[2], "TABLE 2 (Arbeitstitel/Themenquelle)")
dump_cell_paras(tables[3], "TABLE 3 (Genehmigung)")
dump_cell_paras(tables[4], "TABLE 4 (Themendisposition)", max_rows=2)

# body paragraphs 0,1,6,7,10,11 full run info
print("##### BODY PARAGRAPHS #####")
body = doc.find(W + "body")
paras = [c for c in body if tag(c) == "p"]
for idx in (0, 1, 6, 7, 10, 11):
    if idx >= len(paras): continue
    p = paras[idx]
    print(f"--- body p{idx} ---")
    for r in p.findall(W + "r"):
        info = runinfo(r)
        if info:
            print(f"   run: {info}")

# header rels + full anchor
print("\n##### header1.xml.rels #####")
print(open(BASE + "_rels/header1.xml.rels").read())
print("\n##### HEADER ANCHOR (cleaned) #####")
hdr = parse("header1.xml").getroot()
anchor = hdr.find(".//" + W + "hdr/" + W + "p/" + W + "r/" + "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}anchor")
# fallback: find any anchor
if anchor is None:
    for el in hdr.iter():
        if tag(el) == "anchor":
            anchor = el
            break
s = etree.tostring(anchor, pretty_print=True).decode()
s = re.sub(r'\sxmlns:[a-zA-Z0-9]+="[^"]*"', "", s) if (re := __import__("re")) else s
print(s[:3500])