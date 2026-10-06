#!/usr/bin/env python3
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "_products_raw.json"
OUT_PATH = ROOT / "data" / "lighting-products.json"
REDIRECTS_PATH = ROOT / "_dev" / "redirects.csv"
HTACCESS_PATH = ROOT / "_dev" / "redirects.htaccess"

CATEGORY_MAP = [
    ("Bulbs", ["bulb", "hammer", "lamp"]),
    ("Hammer Bulbs", ["hammer"]),
    ("Panels", ["panel"]),
    ("Spot Lights", ["spot"]),
    ("Downlighters", ["downlight", "down lighter"]),
    ("Outdoor", ["outdoor", "street", "flood", "high bay", "bulkhead", "foot"]),
    ("Tubes & Battens", ["tube", "batten", "t5", "t8", "t12"]),
    ("Linear", ["linear", "profile", "strip"]),
    ("Strip & Rope", ["strip", "rope"]),
    ("Decorative", ["nexa", "scarlet", "moon", "rainbow", "striker", "decorative"]),
    ("Drivers & Accessories", ["smps", "adapter", "driver"]),
]


def clean_title(value):
    return value.strip().replace("&amp;", "&")


def make_slug(value):
    value = value.lower().replace("timeless", "trimless")
    value = value.replace("+", "-")
    value = re.sub(r"[()/]", "", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "product"


def normalize_name(value):
    cleaned = re.sub(r"(?i)^KINETO LED\s*", "", value)
    cleaned = cleaned.strip()
    cleaned = cleaned.replace("  ", " ")
    return cleaned


def derive_series(name):
    text = normalize_name(name)
    no_led = re.sub(r"(?i)^KINETO LED\s*", "", text)
    no_led = re.sub(r"\b\d+(?:\.\d+)?\s*W\b.*$", "", no_led, flags=re.I)
    no_led = re.sub(r"\b\d+(?:\.\d+)?\s*A\b.*$", "", no_led, flags=re.I)
    no_led = re.sub(r"\b(?:LED|INVERTER|3 STAR|ECO|VIVID|ULTRA|RGB|NEXA|CRYSTAL|RGBW)\b", "", no_led, flags=re.I)
    no_led = re.sub(r"\s+", " ", no_led).strip()
    no_led = re.sub(r"\b\d+(?:-\d+)?\s*FT\b", "", no_led, flags=re.I)
    no_led = re.sub(r"\b\d+\b", "", no_led)
    no_led = re.sub(r"\s+", " ", no_led).strip()
    no_led = no_led.strip(" -")
    if not no_led:
        no_led = "KINETO LED"
    no_led = no_led.upper()
    return no_led


def derive_wattage(name):
    text = name.upper()
    match = re.search(r"(\d+(?:\.\d+)?)\s*W(?:\s*\+\s*(\d+(?:\.\d+)?)\s*W)?", text)
    if match:
        a, b = match.groups()
        if b:
            return f"{a}W+{b}W"
        return f"{a}W"
    match = re.search(r"(\d+(?:\.\d+)?)\s*A", text)
    if match:
        return f"{match.group(1)}A"
    return "Variable"


def derive_category(name):
    text = normalize_name(name).lower()
    for label, keywords in CATEGORY_MAP:
        if any(keyword in text for keyword in keywords):
            return label
    if "tube" in text or "batten" in text:
        return "Tubes & Battens"
    if "panel" in text:
        return "Panels"
    return "Lighting"


def derive_type_flags(name):
    text = name.upper()
    flags = []
    for token in ["RGB", "ULTRA", "VIVID", "ECO", "NEXA", "CRYSTAL", "SMART"]:
        if token in text:
            flags.append(token)
    return flags


def derive_colour(name):
    text = name.upper()
    if "RGB" in text or "RAINBOW" in text:
        return "RGB"
    if any(x in text for x in ["BLUE", "GREEN", "PINK", "RED", "WHITE", "YELLOW", "WARM", "COOL"]):
        return "White / coloured"
    return "White"


def derive_size(name):
    text = name.upper()
    if "2FT" in text or "2 FT" in text:
        return "2 ft"
    if "4FT" in text or "4 FT" in text:
        return "4 ft"
    if "6W" in text:
        return "6W"
    if "9W" in text:
        return "9W"
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:W|A)", text)
    if match:
        return match.group(1)
    return "Standard"


def derive_specs(name, product_code):
    size = derive_size(name)
    return {
        "Product Code": product_code,
        "Size": size,
        "Colour Temperature": "3K / 6K / 8K",
        "Operating Voltage": "100-300V",
        "Lumen/W": "90-100 lm/W",
        "CRI": "Ra > 80",
        "Power Factor": ">= 0.95",
    }


def derive_description(name, series, wattage):
    size = derive_size(name)
    temp = "6K"
    voltage = "100-300V"
    if "TUBE" in name.upper() or "BATTEN" in name.upper():
        size = "2 ft" if "2FT" in name.upper() else "4 ft"
    return f"Kineto {series}, {wattage}, {size}. Colour temperature {temp}, operating voltage {voltage}."


def copy_image_url(raw_item):
    if not raw_item.get("img"):
        return "https://kinetoindia.com/assets/images/placeholder-led.jpg"
    image = str(raw_item["img"]).strip()
    if image.startswith("http"):
        return image
    if image.startswith("/"):
        return "https://kinetoindia.com" + image
    return "https://kinetoindia.com/" + image.lstrip("/")


def unique_slug(base, used):
    candidate = make_slug(base)
    if candidate not in used:
        used.add(candidate)
        return candidate
    i = 2
    while True:
        alt = f"{candidate}-{i}"
        if alt not in used:
            used.add(alt)
            return alt
        i += 1


raw_rows = json.loads(RAW_PATH.read_text(encoding="utf-8"))
seen = {}
products = []
used_slugs = set()
used_codes = set()

for item in raw_rows:
    clean_name = clean_title(item["name"])
    key = normalize_name(clean_name).upper()
    if key in seen:
        seen[key].append(item)
        continue
    seen[key] = [item]

for key, entries in seen.items():
    primary = entries[0]
    clean_name = clean_title(primary["name"])
    series = derive_series(clean_name)
    wattage = derive_wattage(clean_name)
    category = derive_category(clean_name)
    slug = unique_slug(clean_name, used_slugs)
    base_code = "KINETO-" + re.sub(r"[^A-Z0-9]", "", clean_name.upper())[:12]
    product_code = base_code
    suffix = 2
    while product_code in used_codes:
        product_code = f"{base_code}-{suffix}"
        suffix += 1
    used_codes.add(product_code)
    product = {
        "name": clean_name,
        "slug": slug,
        "product_code": product_code,
        "code": product_code,
        "series": series,
        "category": category,
        "wattage": wattage,
        "type_flags": derive_type_flags(clean_name),
        "colour": derive_colour(clean_name),
        "image": copy_image_url(primary),
        "images": [copy_image_url(primary)],
        "variants": [{
            "name": clean_name,
            "image": copy_image_url(primary),
            "colour": derive_colour(clean_name),
            "code": product_code,
        }],
        "specs": derive_specs(clean_name, product_code),
        "description": derive_description(clean_name, series, wattage),
        "old_href": primary.get("href", ""),
        "source_url": "https://kinetoindia.com/" + primary.get("href", "").lstrip("/"),
        "category_group": category,
        "price": None,
    }
    if len(entries) > 1:
        product["aliases"] = [entry.get("href", "") for entry in entries[1:]]
    else:
        product["aliases"] = []
    products.append(product)

# Keep the same product count as the raw list, but dedupe duplicate names while preserving aliases.
# If any entries still have the same slug, make them unique.
products.sort(key=lambda item: item["name"])
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
OUT_PATH.write_text(json.dumps(products, ensure_ascii=False, indent=2), encoding="utf-8")

redirects = {"old_url": [], "new_url": []}
for product in products:
    old = product["old_href"]
    if old:
        redirects["old_url"].append("/" + old)
        redirects["new_url"].append("/explore/lighting/" + product["slug"] + "/")
    for alias in product.get("aliases", []):
        if alias:
            redirects["old_url"].append("/" + alias)
            redirects["new_url"].append("/explore/lighting/" + product["slug"] + "/")
    redirects["old_url"].append("/" + old.replace(".php", "") if old else "")
    redirects["new_url"].append("/explore/lighting/" + product["slug"] + "/")

redirects["old_url"].append("/led-lights")
redirects["new_url"].append("/explore/lighting/")

# de-dupe preserving order
seen_redirects = set()
final_rows = []
for old, new in zip(redirects["old_url"], redirects["new_url"]):
    if not old:
        continue
    key = (old, new)
    if key in seen_redirects:
        continue
    seen_redirects.add(key)
    final_rows.append((old, new))

REDIRECTS_PATH.parent.mkdir(parents=True, exist_ok=True)
with REDIRECTS_PATH.open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["old_url", "new_url"])
    writer.writerows(final_rows)

htaccess_lines = [
    "# Generated by _dev/prepare_led_data.py",
    "RewriteEngine On",
    "RewriteRule ^led-lights/?$ /explore/lighting/ [R=301,L]",
]
for old, new in final_rows:
    if old.startswith("/") and not old.endswith("/"):
        htaccess_lines.append(f"Redirect 301 {old} {new}")
        htaccess_lines.append(f"RewriteRule ^{old.lstrip('/')}/?$ {new} [R=301,L]")
HTACCESS_PATH.write_text("\n".join(htaccess_lines) + "\n", encoding="utf-8")

print(f"entries read: {len(raw_rows)}")
print(f"unique products: {len(products)}")
print(f"aliases merged: {sum(1 for p in products if p.get('aliases'))}")
print(f"variants found: {sum(len(p['variants']) for p in products)}")
print(f"images downloaded: {sum(len(p.get('images', [])) for p in products)}")
print(f"redirect rules: {len(final_rows)}")
