#!/usr/bin/env python3
"""Final measurements: isolated logo bbox, footer styles/tabs, table row
heights from rendered pages, checkbox inline offsets."""
from lxml import etree
from PIL import Image
import re

BASE = "/home/cloude/from-word-to-latex/_inspect/"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# 1) Isolated logo: region above first text line (y<120pt) on page 1
p = Image.open(BASE + "page-1.png").convert("L")
pw, ph = p.size  # 827x1170 at 100dpi -> 1pt = 100/72 px
ppt = ph / 841.89  # px per pt
crop = p.crop((0, 0, int(pw * 0.5), int(120 * ppt)))
b = crop.point(lambda v: 255 if v < 220 else 0).getbbox()
print(f"isolated logo bbox px: {b}")
if b:
    print(f"  in pt: x={b[0]/ppt:.1f}..{b[2]/ppt:.1f}, y={b[1]/ppt:.1f}..{b[3]/ppt:.1f}")
    print(f"  in cm: x={b[0]/ppt*0.03528:.2f}..{b[2]/ppt*0.03528:.2f}, y={b[1]/ppt*0.03528:.2f}..{b[3]/ppt*0.03528:.2f}")
    print(f"  size: {(b[2]-b[0])/ppt*0.03528:.2f} x {(b[3]-b[1])/ppt*0.03528:.2f} cm")

# 2) Footer styles + tab stops
st = etree.parse(BASE + "word/styles.xml").getroot()
for s in st.findall(W + "style"):
    if s.get(W + "styleId") in ("Fuzeile", "Kopfzeile"):
        print(f"\n===== style {s.get(W+'styleId')} =====")
        raw = etree.tostring(s, pretty_print=True).decode()
        raw = re.sub(r'\sxmlns:[a-zA-Z0-9]+="[^"]*"', "", raw)
        print(raw[:900])

ftr = etree.parse(BASE + "word/footer1.xml").getroot()
print("===== footer paragraphs pPr =====")
for p in ftr.iter(W + "p"):
    ppr = p.find(W + "pPr")
    info = []
    if ppr is not None:
        for el in ppr:
            t = etree.QName(el).localname
            attrs = {k.split("}")[-1]: v for k, v in el.attrib.items()}
            if t == "tabs":
                stops = [{k.split("}")[-1]: (int(v)/567 if v.isdigit() else v) for k, v in s2.attrib.items()} for s2 in el]
                attrs = stops
            info.append(f"{t}={attrs}")
    txt = "".join(x.text or "" for x in p.iter(W + "t"))
    print(f"  {txt[:50]!r}\n    {' '.join(info) if info else '(no pPr)'}")

# 3) footer word positions from bbox html
html = open(BASE + "bbox.html").read()
pages = re.findall(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', html, re.S)
w, h, content = pages[0]
words = re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', content)
print("\n===== footer word coords page 1 (y>770) =====")
for x1, y1, x2, y2, txt in words:
    if float(y1) > 770:
        print(f"  {txt!r:50s} x={float(x1):6.1f}..{float(x2):6.1f} y={float(y1):.1f}")

print("\n===== checkbox/label coords page 1 (table 0 area 165<y<215) =====")
for x1, y1, x2, y2, txt in words:
    if 160 < float(y1) < 215:
        print(f"  {txt!r:30s} x={float(x1):6.1f}..{float(x2):6.1f} y={float(y1):.1f}")