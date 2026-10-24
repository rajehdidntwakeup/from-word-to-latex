#!/usr/bin/env python3
"""Re-extract the embedded fonts and logo from the FH-Burgenland docx.

Word embeds fonts as obfuscated .odttf (the first 32 bytes are XORed with the
fontKey GUID from word/fontTable.xml). This script deobfuscates them to plain
.ttf files usable by XeLaTeX/fontspec, and crops the header logo to its
visible alpha bounding box.

Usage:
    python3 scripts/extract_fonts.py          # run from the repo root

Requires: Pillow (for the logo crop). fontTools is optional (validation).

Licence note: the embedded fonts (Tahoma, Cambria, MS Gothic, Book Antiqua,
Gill Sans MT) are Microsoft/Monotype property. Extract them only for personal
local rendering — never commit or redistribute the .ttf files.
"""
import os
import re
import sys
import uuid
import zipfile

SRC = os.path.join(os.path.dirname(__file__), "..",
                   "01_Ansuchen Zuteilung wiss Arbeit.docx")
FONTS = os.path.join(os.path.dirname(__file__), "..", "latex", "fonts")
ASSETS = os.path.join(os.path.dirname(__file__), "..", "latex", "assets")
os.makedirs(FONTS, exist_ok=True)
os.makedirs(ASSETS, exist_ok=True)

z = zipfile.ZipFile(SRC)
ft = z.read("word/fontTable.xml").decode("utf-8")
rel_xml = z.read("word/_rels/fontTable.xml.rels").decode()
rel_map = dict(re.findall(
    r'Id="(rId\d+)"[^>]*Target="fonts/(font\d+\.odttf)"', rel_xml))

ok = 0
for name, body in re.findall(r'<w:font w:name="([^"]+)">(.*?)</w:font>', ft, re.S):
    for m in re.finditer(r'<w:embed(Regular|Bold|Italic|BoldItalic)\b([^>]*)/>', body):
        kind, attrs = m.group(1), m.group(2)
        rid = re.search(r'r:id="(rId\d+)"', attrs)
        key = re.search(r'w:fontKey="\{([^}]+)\}"', attrs)
        if not (rid and key):
            continue
        fname = rel_map.get(rid.group(1))
        if not fname:
            continue
        raw = z.read("word/fonts/" + fname)
        # Deobfuscation: XOR first 32 bytes with the reversed little-endian
        # byte representation of the fontKey GUID.
        keybytes = uuid.UUID(key.group(1)).bytes_le[::-1]
        data = bytearray(raw)
        for i in range(32):
            data[i] ^= keybytes[i % 16]
        magic = bytes(data[:4])
        if magic not in (b"\x00\x01\x00\x00", b"OTTO", b"true", b"ttcf"):
            print(f"WARNING: {name} {kind}: unexpected magic {magic!r}")
            continue
        out = os.path.join(FONTS, f"{name.replace(' ', '')}-{kind}.ttf")
        with open(out, "wb") as f:
            f.write(bytes(data))
        print(f"{name:14s} {kind:6s} -> {os.path.relpath(out)}")
        ok += 1

# Logo crop
from PIL import Image  # noqa: E402

im = Image.open(z.open("word/media/image1.png"))
alpha = im.getchannel("A")
bbox = alpha.point(lambda a: 255 if a > 0 else 0).getbbox()
im.crop(bbox).save(os.path.join(ASSETS, "fh-logo.png"))
print(f"logo cropped {bbox[2]-bbox[0]}x{bbox[3]-bbox[1]}px -> latex/assets/fh-logo.png")

if ok == 0:
    sys.exit("ERROR: no fonts extracted")
print(f"\n{ok} fonts deobfuscated. Build with: cd latex && xelatex ansuchen.tex")