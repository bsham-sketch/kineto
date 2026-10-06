#!/usr/bin/env python3
"""One-off scrape of kinetoindia.com/led-lights product grid."""
import json
import re
import urllib.request
from html import unescape
from pathlib import Path

URL = "https://kinetoindia.com/led-lights"
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 KinetoRedesign"})
html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
html = re.sub(
    r"(<head\b[^>]*>)",
    r'\1\n<base href="https://kinetoindia.com/" />',
    html,
    count=1,
    flags=re.I,
)
html = re.sub(
    r'<!--\s*<script src="https://code\.jquery\.com/jquery-3\.4\.1\.slim\.min\.js"></script>\s*-->',
    '<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>',
    html,
    count=1,
    flags=re.I,
)
Path("led-lights-live.html").write_text(html, encoding="utf-8")
print("bytes", len(html))

# title / meta
title = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
desc = re.search(r'name=["\']description["\'][^>]*content=["\'](.*?)["\']', html, re.I | re.S)
if not desc:
    desc = re.search(r'content=["\'](.*?)["\'][^>]*name=["\']description["\']', html, re.I | re.S)
canon = re.search(r'rel=["\']canonical["\'][^>]*href=["\'](.*?)["\']', html, re.I)
print("TITLE", unescape(title.group(1).strip()) if title else None)
print("DESC", unescape(desc.group(1).strip()) if desc else None)
print("CANON", canon.group(1) if canon else None)

# banners
for m in re.finditer(r'(https?://[^"\']+led-banner[^"\']+|https?://[^"\']+Kineto_Mob_Banner_Led[^"\']+|[^"\']*led-banner[^"\']*|[^"\']*Mob_Banner_Led[^"\']*)', html, re.I):
    print("BANNER", m.group(1)[:200])

# price list
for m in re.finditer(r'href=["\']([^"\']*price[^"\']*|[^"\']*LED-Lights[^"\']*)["\']', html, re.I):
    print("PDF", m.group(1))

# product cards: look for product links and images
# dump a sample of anchors near product images
imgs = re.findall(r'<img[^>]+>', html, re.I)
print("IMG_TAGS", len(imgs))
for tag in imgs[:8]:
    print("IMG", tag[:300])

anchors = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>', html, re.I)
print("ANCHORS", len(anchors))
php = [a for a in anchors if a.endswith(".php") or ".php" in a]
print("PHP", len(php))
print("SAMPLE PHP", php[:15])
