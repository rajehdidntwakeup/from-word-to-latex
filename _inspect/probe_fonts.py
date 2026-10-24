#!/usr/bin/env python3
"""Deobfuscate all embedded odttf fonts (XOR first 32 bytes with the
fontKey GUID) and save as .ttf; crop the logo PNG."""
import re, uuid, os, zipfile

SRC = "/home/cloude/from-word-to-latex/01_Ansuchen Zuteilung wiss Arbeit.docx"
OUT = "/home/cloude/from-word-to-latex/latex/assets"
FONTS = "/home/cloude/from-word-to-latex/latex/fonts"
os.makedirs(OUT, exist_ok=True)
os.makedirs(FONTS, exist_ok=True)

z = zipfile.ZipFile(SRC)
ft = z.read("word/fontTable.xml").decode("utf-8")
rel_xml = z.read("word/_rels/fontTable.xml.rels").decode()
rel_map = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="fonts/(font\d+\.odttf)"', rel_xml))

results = []
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
        keybytes = uuid.UUID(key.group(1)).bytes_le
        data = bytearray(raw)
        for i in range(32):
            data[i] ^= keybytes[i % 16]
        magic = bytes(data[:4])
        ok = magic in (b"\x00\x01\x00\x00", b"OTTO", b"true", b"ttcf")
        out = f"{FONTS}/{name.replace(' ', '')}-{kind}.ttf"
        with open(out, "wb") as f:
            f.write(bytes(data))
        results.append((name, kind, fname, magic, ok, os.path.getsize(out)))
        print(f"{name:14s} {kind:6s} <- {fname}: magic={magic!r} valid={ok} size={os.path.getsize(out)}")

from PIL import Image
im = Image.open("/home/cloude/from-word-to-latex/_inspect/word/media/image1.png")
alpha = im.getchannel("A")
bbox = alpha.point(lambda a: 255 if a > 0 else 0).getbbox()
cropped = im.crop(bbox)
cropped.save(f"{OUT}/fh-logo.png")
print(f"\nlogo cropped: {cropped.size}px -> {OUT}/fh-logo.png")
print("all fonts valid:", all(r[4] for r in results))