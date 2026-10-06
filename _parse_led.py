#!/usr/bin/env python3
import json
import re
from html import unescape
from pathlib import Path
from collections import Counter

html = Path("led-lights-live.html").read_text(encoding="utf-8")

blocks = re.findall(
    r'<div class="sp-product-col">\s*'
    r'<a href="([^"]+)">\s*'
    r'<img src="([^"]+)">\s*'
    r'</a>\s*'
    r'<div class="sp-product-meta">\s*'
    r'<a href="[^"]+">\s*'
    r'<p>(.*?)</p>',
    html,
    re.S,
)
print("blocks", len(blocks))

products = []
for href, img, name in blocks:
    name = unescape(re.sub(r"\s+", " ", name)).strip()
    products.append({"name": name, "href": href.strip(), "img": img.strip()})

name_c = Counter(p["name"] for p in products)
print("name dups:")
for n, v in name_c.items():
    if v > 1:
        hrefs = [p["href"] for p in products if p["name"] == n]
        imgs = [p["img"] for p in products if p["name"] == n]
        print(v, n)
        print(" ", hrefs)
        print(" ", imgs)

Path("_products_raw.json").write_text(json.dumps(products, indent=2), encoding="utf-8")
print("wrote", len(products), "unique href", len({p["href"] for p in products}))

