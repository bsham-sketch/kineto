#!/usr/bin/env python3
import urllib.request
from pathlib import Path

samples = [
    "05-w-led-bulb.php",
    "9-w-led-bulb-3-star.php",
    "kineto-led-slim-pc-panel-6w-vivid.php",
    "kineto-led-street-light-w-lens-50w-eco.php",
    "kineto-led-flood-light-15w-bc-6kv.php",
    "kineto-led-strip-light-60-led-per-mtr-cw-nw-ww-blue.php",
    "kineto-adapter-4a.php",
    "kineto-led-scarlet-panel-twinlite-3w-3w.php",
]

# discover real slugs from raw json
import json
raw = json.loads(Path("_products_raw.json").read_text(encoding="utf-8"))
print("ALL HREFS:")
for p in raw:
    print(p["href"], "|", p["name"])
