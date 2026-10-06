#!/usr/bin/env python3
import json
import re
import urllib.request
from html import unescape
from pathlib import Path

raw = json.loads(Path("_products_raw.json").read_text(encoding="utf-8"))
# sample a spread of products
indexes = [0, 4, 8, 14, 23, 40, 55, 70, 90, 110, 130, 150]
slugs = []
seen = set()
for i in indexes:
    if i < len(raw):
        slugs.append(raw[i]["href"])
# also one scarlet and one nexa if present
for p in raw:
    if "nexa" in p["name"].lower() or "scarlet" in p["href"]:
        if p["href"] not in slugs:
            slugs.append(p["href"])
            break

out_dir = Path("_samples")
out_dir.mkdir(exist_ok=True)

def fetch(slug):
    url = "https://kinetoindia.com/" + slug
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 KinetoRedesign"})
    try:
        html = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")
    except Exception as e:
        print("FAIL", slug, e)
        return
    Path(out_dir / slug.replace("/", "_")).write_text(html, encoding="utf-8")
    title = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    desc = re.search(r'name=["\']description["\'][^>]*content=["\'](.*?)["\']', html, re.I | re.S)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S)
    print("=" * 60)
    print(slug, "bytes", len(html))
    print("TITLE", unescape(re.sub(r"\s+", " ", title.group(1))).strip() if title else None)
    print("DESC", unescape(re.sub(r"\s+", " ", desc.group(1))).strip()[:300] if desc else None)
    print("H1", unescape(re.sub(r"<[^>]+>", " ", h1.group(1)))[:200] if h1 else None)
    # text-ish content around product
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "\n", text)
    text = unescape(text)
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln and len(ln) > 2]
    # find product name area
    interesting = []
    keys = ("watt", "lumen", "volt", "ip", "cri", "cct", "warranty", "dimension", "feature", "spec", "colour", "color", "application", "know", "description")
    for ln in lines:
        low = ln.lower()
        if any(k in low for k in keys) or "LED" in ln:
            interesting.append(ln)
    # print unique slice
    print("--- INTERESTING ---")
    shown = 0
    prev = ""
    for ln in interesting:
        if ln == prev:
            continue
        prev = ln
        if len(ln) > 240:
            ln = ln[:240]
        print(ln)
        shown += 1
        if shown > 40:
            break

for s in slugs[:8]:
    fetch(s)
print("done samples", len(slugs[:8]))
