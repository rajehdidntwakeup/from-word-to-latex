#!/usr/bin/env python3
"""Phase 2 prep: dump T0/T1 (and T2/T3 for later) completely — every cell:
vAlign, every paragraph with its pPr (spacing, paragraph-MARK rPr incl. size),
and every run's font/size. This explains the rendered row heights."""
from lxml import etree

BASE = "/home/cloude/from-word-to-latex/_inspect/word/"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

def tag(node):
    return etree.QName(node).localname

def attrs(el):
    return {k.split("}")[-1]: v for k, v in el.attrib.items()}

doc = etree.parse(BASE + "document.xml").getroot()
tables = list(doc.iter(W + "tbl"))

def dump_rpr(rpr, ind):
    if rpr is None:
        return
    for el in rpr:
        t = tag(el)
        a = attrs(el)
        if t == "rFonts":
            f = a.get("ascii") or a.get("asciiTheme") or a.get("hAnsi")
            print(f"{ind}    mark rPr rFonts: {f}")
        elif t in ("sz", "szCs"):
            print(f"{ind}    mark rPr {t}: {int(a['val'])/2}pt")

for ti in (0, 1, 2, 3):
    tbl = tables[ti]
    print(f"########## TABLE {ti} ##########")
    for ri, tr in enumerate(tbl.findall(W + "tr")):
        for ci, tc in enumerate(tr.findall(W + "tc")):
            tcPr = tc.find(W + "tcPr")
            va = tcPr.find(W + "vAlign") if tcPr is not None else None
            vas = attrs(va).get("val") if va is not None else "top(default)"
            print(f" r{ri}c{ci} vAlign={vas}:")
            for pi, p in enumerate(tc.findall(W + "p")):
                ppr = p.find(W + "pPr")
                info = []
                if ppr is not None:
                    sp = ppr.find(W + "spacing")
                    if sp is not None:
                        info.append(f"spacing={attrs(sp)}")
                    dump_rpr(ppr.find(W + "rPr"), "      ")
                runs = []
                for r in p.findall(W + "r"):
                    rpr = r.find(W + "rPr")
                    sz, font = None, None
                    if rpr is not None:
                        s = rpr.find(W + "sz")
                        if s is not None: sz = int(s.get(W + "val")) / 2
                        rf = rpr.find(W + "rFonts")
                        if rf is not None:
                            font = rf.get(W + "ascii") or rf.get(W + "asciiTheme")
                    txt = "".join(t.text or "" for t in r.findall(W + "t"))
                    ntabs = len(r.findall(W + "tab"))
                    sdt = len(r.findall(".//" + W + "sdt"))
                    runs.append(f"{txt!r}{'<T>'*ntabs}{f' [sdt:{sdt}]' if sdt else ''} sz={sz} f={font}")
                print(f"    p{pi}: {' '.join(info)} runs={runs if runs else '(EMPTY)'}")
    print()