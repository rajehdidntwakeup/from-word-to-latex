#!/usr/bin/env python3
"""Check tracked changes and ☐ run parents."""
from lxml import etree

BASE = "/home/cloude/from-word-to-latex/_inspect/word/"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

doc = etree.parse(BASE + "document.xml").getroot()

ins_els = list(doc.iter(W + "ins"))
del_els = list(doc.iter(W + "del"))
print(f"tracked insertions: {len(ins_els)}, deletions: {len(del_els)}")

count = 0
for r in doc.iter(W + "r"):
    text = "".join(t.text or "" for t in r.iter(W + "t"))
    if "☐" in text:
        rpr = r.find(W + "rPr")
        fonts = {}
        if rpr is not None:
            rf = rpr.find(W + "rFonts")
            if rf is not None:
                fonts = {k.split('}')[-1]: v for k, v in rf.attrib.items()}
            sz = rpr.find(W + "sz")
            fonts['sz'] = sz.get(W+'val') if sz is not None else None
        parent = r.getparent()
        chain = []
        while parent is not None and etree.QName(parent).localname != "body":
            chain.append(etree.QName(parent).localname)
            parent = parent.getparent()
        count += 1
        if count <= 8:
            print(f"  run text={text!r} fonts={fonts} wrapped_in={chain}")

print(f"total runs with ☐: {count}")

authors = set()
for el in ins_els + del_els:
    authors.add((el.get(W + "author"), el.get(W + "date")))
print("revision authors:", authors)

se = etree.parse(BASE + "settings.xml").getroot()
print("trackChanges flag:", se.find(W + "trackChanges") is not None)