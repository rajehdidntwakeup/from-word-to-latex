#!/usr/bin/env python3
"""Analyze logo PNG alpha bbox + rendered logo position on page 1/2,
and Tabellenraster style borders."""
from lxml import etree
from PIL import Image

BASE = "/home/cloude/from-word-to-latex/_inspect/"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# 1) logo PNG alpha bbox
im = Image.open(BASE + "word/media/image1.png")
alpha = im.getchannel("A")
bbox = alpha.getbbox()  # non-zero alpha region
w, h = im.size
print(f"image1.png {w}x{h}, alpha bbox={bbox}")
if bbox:
    bx1, by1, bx2, by2 = bbox
    print(f"  visible content: {bx2-bx1}x{by2-by1}px = {(bx2-bx1)/96*2.54:.2f}x{(by2-by1)/96*2.54:.2f}cm at 96dpi")
    print(f"  fractions: left={bx1/w:.3f} top={by1/h:.3f} right={1-bx2/w:.3f} bottom={1-by2/h:.3f}")

# opaque-only bbox (alpha > 240)
mask = alpha.point(lambda a: 255 if a > 200 else 0)
bbox2 = mask.getbbox()
print(f"  opaque(>200) bbox={bbox2}")

# 2) rendered pages: find dark pixels in top-left quadrant
for pg in (1, 2):
    p = Image.open(f"{BASE}page-{pg}.png").convert("RGB")
    pw, ph = p.size
    # crop top-left 45% x 40%
    crop = p.crop((0, 0, int(pw * 0.45), int(ph * 0.40)))
    g = crop.convert("L")
    # bbox of pixels darker than 200
    b = g.point(lambda v: 255 if v < 200 else 0).getbbox()
    print(f"page-{pg}: size {pw}x{ph}, dark-content bbox in top-left crop: {b}")
    if b:
        scale = 595.3 / pw  # pt per px (100dpi render: 1pt=100/72px≈1.389)
        print(f"  -> in pt: x={b[0]*595.3/pw:.1f}..{b[2]*595.3/pw:.1f}, y={b[1]*841.9/ph:.1f}..{b[3]*841.9/ph:.1f}")
        print(f"  -> in cm: x={b[0]*21.0/pw:.2f}..{b[2]*21.0/pw:.2f}, y={b[1]*29.7/ph:.2f}..{b[3]*29.7/ph:.2f}")

# 3) Tabellenraster style
st = etree.parse(BASE + "word/styles.xml").getroot()
for s in st.findall(W + "style"):
    sid = s.get(W + "styleId")
    if sid in ("Tabellenraster",):
        print(f"\n===== style {sid} =====")
        print(etree.tostring(s, pretty_print=True).decode()[:1500].replace('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" ', ""))

# any other styles used? list all styleIds defined
ids = [s.get(W + "styleId") for s in st.findall(W + "style")]
print("\nall defined styles:", ids)

# 4) colors used in logo (sample dominant dark colors)
im2 = Image.open(BASE + "word/media/image1.png").convert("RGBA")
px = im2.load()
from collections import Counter
c = Counter()
for y in range(0, h, 20):
    for x in range(0, w, 20):
        r, g, b, a = px[x, y]
        if a > 200:
            c[(r // 32 * 32, g // 32 * 32, b // 32 * 32)] += 1
print("\nlogo dominant colors (quantized):", c.most_common(6))