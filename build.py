#!/usr/bin/env python3
"""
Kineto India — static site generator.

Writes every page in the site from the shared chrome below. Plain HTML and CSS
come out the other end; this script is only here so the header, mega menu,
footer and quick bar can't drift apart across ten pages.

    python3 build.py
"""

import csv
import os
import re
import html
import json
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))

PHONE = "+911800000000"
PHONE_DISPLAY = "1800 000 000"
WHATSAPP = "https://wa.me/911800000000"
EMAIL = "hello@kinetoindia.com"
TAGLINE = "High performance. Every connection."
SHOW_PRICE = False
SITE_URL = "https://kinetoindia.com"
NOINDEX = True
PRICE_LIST_URL = "https://kinetoindia.com/downloads/price-lists/LED-Lights-List.pdf"

# ---------------------------------------------------------------------------
# Content model
# ---------------------------------------------------------------------------

CATEGORIES = [
    {
        "slug": "wires", "num": "01", "name": "Wires &amp; Cables", "plain": "Wires &amp; Cables",
        "personality": "Strong. Tough. Protective.",
        "statement": "The strength you never see.",
        "tone": "copper", "image": "cat-wires.jpg",
        "story": [
            ("What you see is a wire.",
             "A quiet line behind the wall. It is asked to carry everything, every day, without ever being noticed."),
            ("What you don&rsquo;t see is everything that protects you.",
             "Layers of insulation engineered to resist heat, flame and time. Built so a family never has to think about it."),
            ("The strength is inside.",
             "Bright, high-conductivity copper drawn in-house. Every strand accountable for the load it carries."),
        ],
        "tech": [
            ("In-house copper drawing", "Conductor purity controlled from rod to strand."),
            ("Flame-retardant insulation", "Formulated to slow fire and resist heat build-up."),
            ("Tested per coil", "Every batch checked for conductivity and insulation strength."),
        ],
        "range": ["XTREME", "FORCE", "FLEXIBLE", "INDUSTRIAL"],
        "meta": "Kineto Wires &amp; Cables: Strong. Tough. Protective. Bright, high-conductivity copper drawn in-house. Every strand accountable for the load it carries.",
    },
    {
        "slug": "lighting", "num": "02", "name": "Lighting", "plain": "Lighting",
        "personality": "Optimistic. Beautiful. Transformative.",
        "statement": "Change what you see.",
        "tone": "glow", "image": "cat-lighting.jpg",
        "story": [
            ("Before light, there is only space.",
             "Walls. Corners. A room waiting for a reason to be seen."),
            ("Light decides how a place feels.",
             "Warm or crisp. Focused or open. The same room, transformed by what shines on it."),
            ("Change what you see.",
             "Efficient LED engineering with colour that stays true, built to shine for years."),
        ],
        "tech": [
            ("High-CRI LEDs", "Colours look the way they were meant to."),
            ("Surge protection", "Designed for real Indian voltage conditions."),
            ("Thermal management", "Cool-running drivers for long life."),
        ],
        "range": ["PANELS", "DOWNLIGHTS", "BATTENS", "OUTDOOR", "DECORATIVE"],
        "meta": "Kineto Lighting: Optimistic. Beautiful. Transformative. Efficient LED engineering with colour that stays true.",
    },
    {
        "slug": "switchgear", "num": "03", "name": "Switchgear", "plain": "Switchgear",
        "personality": "Technical. Intelligent. Protective.",
        "statement": "Protection should never compromise.",
        "tone": "steel", "image": "cat-switchgear.jpg",
        "story": [
            ("Every circuit has a moment of danger.",
             "A surge. A short. A fault that lasts less than a heartbeat."),
            ("That moment decides everything.",
             "Precision mechanisms that trip in milliseconds, before heat becomes harm."),
            ("Protection should never compromise.",
             "Engineered contacts, calibrated trips and enclosures built to be trusted for decades."),
        ],
        "tech": [
            ("Precision trip mechanisms", "Consistent response across thousands of operations."),
            ("Arc-resistant chambers", "Fault energy contained, every time."),
            ("Modular systems", "MCBs, RCCBs and distribution boards that fit together."),
        ],
        "range": ["MCB", "RCCB", "ISOLATORS", "DISTRIBUTION BOARDS"],
        "meta": "Kineto Switchgear: Technical. Intelligent. Protective. Precision trip mechanisms, arc-resistant chambers and modular distribution systems.",
    },
    {
        "slug": "fans", "num": "04", "name": "Fans", "plain": "Fans",
        "personality": "Movement. Comfort. Design.",
        "statement": "Performance you can feel.",
        "tone": "breeze", "image": "cat-fans.jpg",
        "story": [
            ("Air is invisible.",
             "Until it moves. Then you feel it on your skin and the day changes."),
            ("Movement is engineered.",
             "Blade angle, motor torque, balance. The difference between noise and comfort."),
            ("Performance you can feel.",
             "High air delivery, low power draw, silhouettes designed to belong in modern Indian homes."),
        ],
        "tech": [
            ("High air-delivery blades", "Aerodynamic profiles that push more air, quietly."),
            ("Energy-efficient motors", "Lower bills without lower comfort."),
            ("Dynamic balancing", "Smooth at every speed."),
        ],
        "range": ["CEILING", "PEDESTAL", "TABLE", "EXHAUST"],
        "meta": "Kineto Fans: Movement. Comfort. Design. High air delivery, low power draw, designed for modern Indian homes.",
    },
]

SOLAR = {
    "num": "05", "name": "Solar",
    "statement": "Don&rsquo;t wait for the future. Power it.",
    "tone": "sun", "image": "cat-solar.jpg",
}

SOLUTIONS = [
    ("home", "My Home", "Your Home", "Safe walls. Bright rooms. Quiet comfort.",
     ["Wires", "Lighting", "Fans", "Switchgear", "Safety Solutions"]),
    ("business", "My Business", "Your Business", "Every hour open is an hour earning.",
     ["Commercial Lighting", "Switchgear", "Flexible Cables", "Fans", "Rooftop Solar"]),
    ("industry", "My Industry", "Your Industry", "Downtime is the most expensive thing you buy.",
     ["Industrial Cables", "Distribution Boards", "High-Bay Lighting", "Exhaust Systems", "Solar Plants"]),
    ("future", "My Future", "Your Future", "Own the energy you use.",
     ["Kineto Solar Rooftop", "Inverters &amp; Storage", "Net Metering Support", "Savings Planning"]),
]

PROOF = [
    ("factory", "Factory", "Built with precision.", "proof-factory.jpg"),
    ("testing", "Testing", "Tested for performance.", "proof-testing.jpg"),
    ("people", "People", "Powered by expertise.", "proof-people.jpg"),
    ("market", "Market", "Trusted connections.", "proof-market.jpg"),
    ("technology", "Technology", "Built for what&rsquo;s next.", "proof-technology.jpg"),
]

STORIES = [
    ("I install hundreds of connections. My name is on every recommendation I make.",
     "Electrician", "Bihar"),
    ("Customers come back for the second floor. That only happens when the first floor never gave trouble.",
     "Retailer", "Uttar Pradesh"),
    ("On the line, we don&rsquo;t call it a wire. We call it someone&rsquo;s home.",
     "Factory Technician", "Kineto Plant"),
    ("Our rooftop went from a bill to an asset. That changes how a family thinks.",
     "Solar Customer", "Rajasthan"),
]

AUDIENCES = [
    ("Consumer", "Find a product", "/explore/"),
    ("Retailer", "Find a distributor", "/connect/"),
    ("Distributor", "Become a partner", "/connect/"),
    ("Electrician", "Join Kineward", "/connect/"),
    ("Builder", "Project enquiry", "/connect/"),
    ("Solar customer", "Calculate savings", "/future/"),
]

CITIES = ["Delhi", "Mumbai", "Kolkata", "Patna", "Lucknow", "Jaipur",
          "Ahmedabad", "Hyderabad", "Bengaluru", "Chennai", "Guwahati", "Bhopal"]

PILLARS = [
    ("Independence", "Generate on your own roof. Depend less on the grid and on rising tariffs."),
    ("Optimism", "A bill becomes an asset. Sunlight becomes a plan for the next 25 years."),
    ("Future", "Net metering, storage and EV-ready design, engineered for what&rsquo;s next."),
]

NAV = [("Explore", "/explore/"), ("Solutions", "/solutions/"),
       ("Why Kineto", "/why-kineto/"), ("Future", "/future/")]

FOOTER_NAV = [("01", "Believe", "/why-kineto/"), ("02", "Explore", "/explore/"),
              ("03", "Solve", "/solutions/"), ("04", "Connect", "/connect/"),
              ("05", "Future", "/future/")]

MENU = [
    ("Products", [
        ("01", "Wires &amp; Cables", "/explore/wires/", "copper"),
        ("02", "Lighting", "/explore/lighting/", "glow"),
        ("03", "Switchgear", "/explore/switchgear/", "steel"),
        ("04", "Fans", "/explore/fans/", "breeze"),
    ]),
    ("Ecosystem", [
        ("05", "Kineward", "/connect/#kineward", "primary"),
        ("06", "Solar", "/future/", "sun"),
        ("07", "Partner with us", "/connect/#partner", "primary"),
    ]),
    ("Company", [
        ("08", "Our Story", "/why-kineto/", "steel"),
        ("09", "Stories", "/why-kineto/#stories", "steel"),
        ("10", "Contact", "/connect/#contact", "primary"),
    ]),
]

ICONS = {
    "phone": '<path d="M13.832 16.568a1 1 0 0 0 1.213-.303l.355-.465A2 2 0 0 1 17 15h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2A18 18 0 0 1 2 4a2 2 0 0 1 2-2h3a2 2 0 0 1 2 2v3a2 2 0 0 1-.8 1.6l-.468.351a1 1 0 0 0-.292 1.233 14 14 0 0 0 6.392 6.384"/>',
    "map-pin": '<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>',
    "message-circle": '<path d="M2.992 16.342a2 2 0 0 1 .094 1.167l-1.065 3.29a1 1 0 0 0 1.236 1.168l3.413-.998a2 2 0 0 1 1.099.092 10 10 0 1 0-4.777-4.719"/>',
    "book-open": '<path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>',
}


def icon(name):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            + ICONS[name] + "</svg>")


# ---------------------------------------------------------------------------
# Chrome
# ---------------------------------------------------------------------------

def header(active):
    nav = "\n".join(
        '          <a href="%s" class="label"%s>%s</a>'
        % (href, ' aria-current="page"' if href == active else "", label)
        for label, href in NAV
    )

    washes = "\n".join(
        '      <span class="menu__wash wash-%s" data-wash="%s"></span>' % (tone, num)
        for _, items in MENU for num, _, _, tone in items
    )

    cols = []
    for title, items in MENU:
        links = "\n".join(
            '            <li><a href="%s" class="menu__link" data-wash="%s">'
            '<span class="label">%s</span>'
            '<span class="display-md">%s</span></a></li>' % (href, num, num, label)
            for num, label, href, _ in items
        )
        cols.append(
            '        <div>\n'
            '          <p class="eyebrow mb-6">%s</p>\n'
            '          <ul>\n%s\n          </ul>\n'
            '        </div>' % (title, links)
        )

    return """  <div class="rail" aria-hidden="true">
    <span class="rail__fill" data-rail-fill></span>
    <span class="rail__glow energy-line"></span>
  </div>

  <header class="site-header">
    <div class="site-header__inner">
      <a href="/" class="wordmark">Kineto</a>
      <nav class="site-nav" aria-label="Primary">
%s
      </nav>
      <button type="button" class="burger" data-menu-toggle aria-label="Open menu" aria-expanded="false" aria-controls="menu">
        <span></span>
        <span></span>
      </button>
    </div>
  </header>

  <div class="menu" id="menu" aria-hidden="true">
%s
    <div class="menu__grain grain"></div>
    <div class="menu__inner">
      <div class="menu__cols">
%s
      </div>
      <div class="menu__sign">
        <span class="spark-dot"></span>
        <span class="label">%s</span>
      </div>
    </div>
  </div>
""" % (nav, washes, "\n".join(cols), TAGLINE)


def footer():
    links = "\n".join(
        '        <li><a href="%s"><span class="label">%s</span>'
        '<span class="display-sm">%s</span></a></li>' % (href, num, label)
        for num, label, href in FOOTER_NAV
    )

    return """  <footer class="site-footer">
    <div class="site-footer__top">
      <div>
        <p class="display-xl">Kineto</p>
        <p class="label mt-6">%s</p>
      </div>
      <ul class="site-footer__nav">
%s
      </ul>
    </div>
    <div class="site-footer__base label">
      <span>&copy; <span data-year>2026</span> Kineto India</span>
      <span>Made in India</span>
    </div>
  </footer>

  <nav class="quickbar" aria-label="Quick actions">
    <a href="tel:%s">%s Call</a>
    <a href="/connect/#dealer">%s Dealer</a>
    <a href="%s" target="_blank" rel="noreferrer">%s WhatsApp</a>
    <a href="/explore/">%s Catalogue</a>
  </nav>
""" % (TAGLINE, links, PHONE, icon("phone"), icon("map-pin"),
       WHATSAPP, icon("message-circle"), icon("book-open"))


def page(title, description, body, active="", extra_class="", canonical=None, jsonld="", robots=None):
    if canonical is None and active == "/":
        canonical_url = SITE_URL + "/"
    else:
        canonical_url = canonical
    canonical_tag = '<link rel="canonical" href="%s">' % canonical_url if canonical_url else ""
    robots_tag = '<meta name="robots" content="noindex">' if (robots is not None and robots) or NOINDEX else ""
    jsonld_tag = ('<script type="application/ld+json">%s</script>' % jsonld) if jsonld else ""
    return """<!DOCTYPE html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="author" content="Kineto India">
<meta name="description" content="%s">
<meta name="theme-color" content="#0a0a0a">
<meta property="og:type" content="website">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta name="twitter:card" content="summary_large_image">
%s
%s
%s
<link rel="icon" href="/assets/favicon.ico" type="image/x-icon">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:ital,wdth,wght@0,62..125,100..900;1,62..125,100..900&amp;display=swap">
<link rel="stylesheet" href="/css/styles.css">
</head>
<body%s>
%s
  <main>
%s
  </main>

%s
  <script src="/js/main.js"></script>
%s
</body>
</html>
""" % (title, description, title, description,
       canonical_tag, robots_tag, jsonld_tag,
       (' class="%s"' % extra_class) if extra_class else "",
       header(active), body, footer(), "")


def relativize(content, depth):
    """Rewrite root-relative URLs as document-relative ones.

    Pages are authored with absolute paths ("/explore/wires/") because that is
    easier to read, then rewritten here to "../../explore/wires/" so the site
    runs from any folder: a domain root, a subdirectory like /kineto/, or a
    local file:// preview. `depth` is how many directories deep the page sits.
    """
    prefix = "../" * depth

    def swap(match):
        attr, path = match.group(1), match.group(2)
        if path == "/":
            return '%s="%s"' % (attr, prefix if prefix else "./")
        return '%s="%s%s"' % (attr, prefix, path.lstrip("/"))

    # Only touches site-root paths; https:, mailto: and tel: are left alone.
    return re.sub(r'\b(href|src)="(/[^"]*)"', swap, content)


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    depth = path.count("/")
    with open(full, "w", encoding="utf-8") as f:
        f.write(relativize(content, depth))
    print("  wrote", path)


def section_head(num, eyebrow=None, rule="rule", dot=False):
    bits = ['    <div class="reveal section-head">']
    if num:
        bits.append('      <span class="label">%s</span>' % num)
    bits.append('      <span class="%s"></span>' % rule)
    if eyebrow:
        bits.append('      <span class="eyebrow">%s</span>' % eyebrow)
    if dot:
        bits.append('      <span class="spark-dot"></span>')
    bits.append("    </div>")
    return "\n".join(bits)


def load_catalogue(path="data/lighting-products.json"):
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return []
    try:
        with open(full, "r", encoding="utf-8") as f:
            products = json.load(f)
    except Exception:
        return []
    return products if isinstance(products, list) else []


def catalogue_sort_key(product, mode):
    value = product.get("wattage") or "0"
    num = 0
    match = re.search(r"(\d+(?:\.\d+)?)", str(value))
    if match:
        num = float(match.group(1))
    if mode == "name":
        return (product.get("name") or "").lower(), num
    return (num, (product.get("name") or "").lower())


def build_catalogue(category, products):
    def product_badges(product):
        badges = []
        for flag in (product.get("type_flags") or [])[:3]:
            badges.append('<span class="catalogue__badge">%s</span>' % html.escape(flag))
        if product.get("colour"):
            badges.append('<span class="catalogue__badge catalogue__badge--soft">%s</span>' % html.escape(str(product.get("colour"))))
        return "".join(badges)

    def product_card(product):
        wa = product.get("wattage") or "Variable"
        name = html.escape(str(product.get("name") or "Product"))
        series = html.escape(str(product.get("series") or "Series"))
        slug = product.get("slug") or "product"
        image = product.get("image") or "/assets/cat-lighting.jpg"
        href = "/explore/lighting/%s/" % slug
        speak = "Hi, I'd like to enquire about %s (%s)" % (
            product.get("name") or "this product",
            product.get("code") or "",
        )
        enquire = "https://wa.me/911800000000?text=%s" % quote(speak)
        return '''
          <article class="catalogue__card" data-catalogue-card data-name="%s" data-series="%s" data-category="%s" data-type="%s" data-colour="%s" data-wattage="%s" data-search="%s">
            <div class="catalogue__media">
              <img src="%s" alt="%s LED light by Kineto" width="900" height="900" loading="lazy">
            </div>
            <div class="catalogue__body">
              <p class="label">%s</p>
              <h3 class="display-sm">%s</h3>
              <div class="catalogue__meta">
                <span class="catalogue__meta-item">%s</span>
                <span class="catalogue__meta-item">%s</span>
              </div>
              <div class="catalogue__badges">%s</div>
              <div class="catalogue__actions">
                <a href="%s" class="catalogue__action catalogue__action--primary">View details</a>
                <a href="%s" class="catalogue__action" target="_blank" rel="noreferrer">Enquire</a>
              </div>
            </div>
          </article>
        ''' % (
            html.escape(str(product.get("name") or "")),
            html.escape(str(product.get("series") or "")),
            html.escape(str(product.get("category") or "")),
            " ".join(html.escape(str(tag)) for tag in (product.get("type_flags") or [])),
            html.escape(str(product.get("colour") or "")),
            str(product.get("wattage") or "0"),
            html.escape(str(product.get("name") or "") + " " + str(product.get("series") or "")),
            image,
            html.escape(str(product.get("name") or "Product")),
            series,
            name,
            html.escape(str(product.get("category") or "Lighting")),
            html.escape(str(wa)),
            product_badges(product),
            href,
            enquire,
        )

    sorted_products = sorted(products, key=lambda p: catalogue_sort_key(p, "name"))
    grouped = {}
    for product in sorted_products:
        group_key = product.get("category") or "Lighting"
        grouped.setdefault(group_key, []).append(product)

    category_options = []
    seen_categories = set()
    for product in sorted_products:
        group_key = product.get("category") or "Lighting"
        if group_key in seen_categories:
            continue
        seen_categories.add(group_key)
        category_options.append(
            '<button type="button" class="catalogue__toggle" data-catalogue-filter="category" data-filter-value="%s">%s</button>'
            % (html.escape(group_key), html.escape(group_key))
        )

    series_options = []
    seen_series = set()
    for product in sorted_products:
        series = str(product.get("series") or "Series")
        if series in seen_series:
            continue
        seen_series.add(series)
        series_options.append(
            '<button type="button" class="catalogue__toggle" data-catalogue-filter="series" data-filter-value="%s">%s</button>'
            % (html.escape(series), html.escape(series))
        )

    wattage_options = [
        '<button type="button" class="catalogue__toggle" data-catalogue-filter="wattage" data-filter-value="0-5">Up to 5W</button>',
        '<button type="button" class="catalogue__toggle" data-catalogue-filter="wattage" data-filter-value="5-10">5W to 10W</button>',
        '<button type="button" class="catalogue__toggle" data-catalogue-filter="wattage" data-filter-value="10-25">10W to 25W</button>',
        '<button type="button" class="catalogue__toggle" data-catalogue-filter="wattage" data-filter-value="25+">25W &amp; above</button>'
    ]

    colour_options = [
        '<button type="button" class="catalogue__toggle" data-catalogue-filter="colour" data-filter-value="White">White</button>',
        '<button type="button" class="catalogue__toggle" data-catalogue-filter="colour" data-filter-value="RGB">RGB</button>',
        '<button type="button" class="catalogue__toggle" data-catalogue-filter="colour" data-filter-value="White / coloured">White / coloured</button>',
    ]

    groups_html = []
    for group_key in sorted(grouped):
        cards = "\n".join(product_card(p) for p in grouped[group_key])
        groups_html.append(
            '<section class="catalogue__group" data-catalogue-group="%s">\n'
            '  <div class="catalogue__group-head">\n'
            '    <span class="eyebrow">%s</span>\n'
            '    <span class="label">%s products</span>\n'
            '  </div>\n'
            '  <div class="catalogue__grid">%s</div>\n'
            '</section>' % (
                html.escape(group_key),
                html.escape(group_key),
                len(grouped[group_key]),
                cards,
            )
        )

    lighting_story = "\n".join(
        '    <section class="chapter">\n'
        '      <div class="chapter__grid">\n'
        '        <div class="reveal"><span class="label">%02d / %02d</span></div>\n'
        '        <div>\n'
        '          <div class="reveal"><h2 class="display-lg">%s</h2></div>\n'
        '          <div class="reveal mt-8" data-delay="200"><p class="body-lg">%s</p></div>\n'
        '        </div>\n'
        '      </div>\n'
        '    </section>' % (n + 1, len(CATEGORIES[1]["story"]), title, text)
        for n, (title, text) in enumerate(CATEGORIES[1]["story"])
    )

    tech = "\n".join(
        '        <div class="reveal tech-card" data-delay="%d">\n'
        '          <span class="tech-card__rule rule-glow"></span>\n'
        '          <h3 class="display-sm">%s</h3>\n'
        '          <p class="body mt-4">%s</p>\n'
        '        </div>' % (n * 100, title, text)
        for n, (title, text) in enumerate(CATEGORIES[1]["tech"])
    )

    body = '''
    <section class="hero-page">
      <img src="/assets/cat-lighting.jpg" alt="Lighting" width="1280" height="800" class="img-dim hero-page__img--spin">
      <span class="hero-page__scrim"></span>
      <div class="hero-page__body">
        <p class="eyebrow mb-6">02 &middot; Lighting</p>
        <h1 class="display-xl">Change what you see.</h1>
        <p class="label mt-8 text-glow">Optimistic. Beautiful. Transformative.</p>
      </div>
    </section>

    <section class="section section--top catalogue-wrap" data-catalogue>
      <div class="catalogue__topbar">
        <div>
          <p class="eyebrow mb-6">02 &middot; Explore</p>
          <h1 class="display-xl">Lighting catalogue.</h1>
        </div>
        <a href="%s" class="link link--spark label">Download price list &rarr;</a>
      </div>
      <nav class="catalogue__crumbs" aria-label="Breadcrumb">
        <a href="/">Home</a>
        <span>/</span>
        <a href="/explore/">Explore</a>
        <span>/</span>
        <span aria-current="page">Lighting</span>
      </nav>
      <div class="catalogue__controls">
        <div class="catalogue__search-wrap">
          <label class="visually-hidden" for="catalogue-search">Search products</label>
          <input id="catalogue-search" type="search" value="" placeholder="Search by name or series" data-catalogue-search>
        </div>
        <label class="catalogue__sort">
          <span class="label">Sort</span>
          <select data-catalogue-sort>
            <option value="name">Name A-Z</option>
            <option value="wattage-asc">Wattage low-high</option>
            <option value="wattage-desc">Wattage high-low</option>
          </select>
        </label>
      </div>
      <div class="catalogue__status">
        <p class="label" aria-live="polite" data-catalogue-results>%s products</p>
        <button type="button" class="catalogue__drawer-toggle" data-catalogue-drawer-toggle aria-expanded="false">Filters</button>
      </div>
      <div class="catalogue__layout">
        <aside class="catalogue__sidebar" data-catalogue-sidebar>
          <div class="catalogue__sidebar-head">
            <h2 class="display-sm">Filters</h2>
            <button type="button" class="catalogue__clear" data-catalogue-clear>Clear all</button>
          </div>
          <div class="catalogue__filter-block">
            <p class="eyebrow">Category</p>
            <div class="catalogue__filter-row">%s</div>
          </div>
          <div class="catalogue__filter-block">
            <p class="eyebrow">Series / type</p>
            <div class="catalogue__filter-row">%s</div>
          </div>
          <div class="catalogue__filter-block">
            <p class="eyebrow">Wattage range</p>
            <div class="catalogue__filter-row">%s</div>
          </div>
          <div class="catalogue__filter-block">
            <p class="eyebrow">Colour</p>
            <div class="catalogue__filter-row">%s</div>
          </div>
        </aside>
        <div class="catalogue__main">
          <div class="catalogue__chips" data-catalogue-chips></div>
          <div class="catalogue__empty" data-catalogue-empty hidden>
            <p class="display-sm">No lighting products match your filters.</p>
            <button type="button" class="catalogue__clear catalogue__clear--large" data-catalogue-clear>Clear all</button>
          </div>
          %s
        </div>
      </div>
    </section>

    <section class="section bordered">
      <div class="reveal">
        <p class="eyebrow mb-6">Technology</p>
        <h2 class="display-md">Built into every unit.</h2>
      </div>
      <div class="hairgrid cols-md-3 mt-14">
%s
      </div>
    </section>

%s

    <a href="/explore/switchgear/" class="next-world">
      <span class="label">Next world &middot; 03</span>
      <span class="display-lg next-world__name">Switchgear &rarr;</span>
    </a>
    ''' % (
        PRICE_LIST_URL,
        len(sorted_products),
        "".join(category_options),
        "".join(series_options),
        "".join(wattage_options),
        "".join(colour_options),
        "\n".join(groups_html),
        tech,
        lighting_story,
    )

    canonical_url = SITE_URL + "/explore/lighting/"
    breadcrumb_jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "Explore", "item": SITE_URL + "/explore/"},
            {"@type": "ListItem", "position": 3, "name": "Lighting", "item": canonical_url},
        ],
    }, ensure_ascii=False)
    item_list = json.dumps({
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Lighting products",
        "itemListOrder": "Unordered",
        "numberOfItems": len(sorted_products),
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "url": SITE_URL + "/explore/lighting/%s/" % p.get("slug")}
            for i, p in enumerate(sorted_products[:20])
        ],
    }, ensure_ascii=False)
    write("explore/lighting/index.html", page(
        "Lighting catalogue &mdash; Kineto India",
        "LED lighting catalogue from Kineto: panels, downlighters, battens, outdoor lights and decorative lighting for homes, businesses and projects.",
        body,
        active="/explore/",
        canonical=canonical_url,
        jsonld=item_list,
        robots=NOINDEX,
    ))


def build_product_pages(products):
    for product in products:
        name = product.get("name") or "Kineto product"
        product_code = product.get("code") or product.get("product_code") or "KINETO"
        slug = product.get("slug") or "product"
        category = product.get("category") or "Lighting"
        series = product.get("series") or "Lighting"
        variants = product.get("variants") or [{"name": name, "image": product.get("image"), "colour": product.get("colour") or "White", "code": product_code}]
        thumbnails = "".join(
            '<button type="button" class="catalogue__thumb" data-product-thumb="%s" data-product-image="%s" aria-label="Show %s variant"><img src="%s" alt="%s" width="220" height="220" loading="lazy"></button>'
            % (idx, variant.get("image") or product.get("image"), html.escape(str(variant.get("name") or name)), variant.get("image") or product.get("image"), html.escape(str(variant.get("name") or name)))
            for idx, variant in enumerate(variants)
        )
        current_image = variants[0].get("image") or product.get("image") or "/assets/cat-lighting.jpg"
        spec_rows = product.get("specs") or {}
        dl_rows = "".join(
            '<div><dt>%s</dt><dd>%s</dd></div>' % (html.escape(str(key)), html.escape(str(value)))
            for key, value in spec_rows.items()
        )
        siblings = [p for p in products if p.get("series") == series and p.get("slug") != slug]
        sibling_rows = "".join(
            '<a href="/explore/lighting/%s/" class="catalogue__sibling">%s <span>%s</span></a>' % (
                p.get("slug") or "product",
                html.escape(str(p.get("name") or "Product")),
                html.escape(str(p.get("wattage") or "")),
            )
            for p in siblings[:4]
        )
        related = [p for p in products if p.get("category") == category and p.get("slug") != slug][:4]
        related_cards = "".join(
            '<a href="/explore/lighting/%s/" class="catalogue__related-card">\n'
            '  <img src="%s" alt="%s LED light by Kineto" width="220" height="220" loading="lazy">\n'
            '  <span class="label">%s</span>\n'
            '  <span class="display-sm">%s</span>\n'
            '</a>' % (
                p.get("slug") or "product",
                p.get("image") or "/assets/cat-lighting.jpg",
                html.escape(str(p.get("name") or "Product")),
                html.escape(str(p.get("category") or "Lighting")),
                html.escape(str(p.get("name") or "Product")),
            )
            for p in related
        )
        whatsapp = "https://wa.me/911800000000?text=%s" % quote("Hi, I'd like to enquire about %s (%s)" % (name, product_code))
        mailto = "mailto:hello@kinetoindia.com?subject=%s" % quote("Enquiry for %s" % name)
        body = '''
    <section class="section section--top catalogue-product">
      <nav class="catalogue__crumbs" aria-label="Breadcrumb">
        <a href="/">Home</a>
        <span>/</span>
        <a href="/explore/">Explore</a>
        <span>/</span>
        <a href="/explore/lighting/">Lighting</a>
        <span>/</span>
        <span aria-current="page">%s</span>
      </nav>
      <div class="catalogue__product-layout">
        <div class="catalogue__gallery-wrap">
          <div class="catalogue__gallery-main">
            <img src="%s" alt="%s LED light by Kineto" width="900" height="900" data-product-main>
          </div>
          <div class="catalogue__thumbs">%s</div>
        </div>
        <div class="catalogue__detail">
          <p class="eyebrow">%s</p>
          <h1 class="display-lg">%s</h1>
          <div class="catalogue__detail-meta">
            <span class="catalogue__meta-item">Product code: %s</span>
            <span class="catalogue__meta-item">%s</span>
          </div>
          <div class="catalogue__badges">%s</div>
          <p class="body-lg mt-8">%s</p>
          <div class="catalogue__cta-row">
            <a href="%s" class="catalogue__action catalogue__action--primary" target="_blank" rel="noreferrer">Enquire</a>
            <a href="%s" class="catalogue__action">Download price list</a>
            <a href="tel:+911800000000" class="catalogue__action">Call</a>
          </div>
          <div class="catalogue__specs">
            <h2 class="display-sm">Specifications</h2>
            <dl>%s</dl>
          </div>
        </div>
      </div>
      <div class="catalogue__sibling-box">
        <p class="eyebrow">Other wattages in this series</p>
        <div class="catalogue__sibling-list">%s</div>
      </div>
    </section>
    <section class="section bordered">
      <div class="reveal">
        <p class="eyebrow mb-6">Related products</p>
        <h2 class="display-lg">More in %s</h2>
      </div>
      <div class="catalogue__related-grid">%s</div>
    </section>
    ''' % (
        html.escape(name),
        current_image,
        html.escape(name),
        thumbnails,
        html.escape(category),
        html.escape(name),
        html.escape(product_code),
        html.escape(series),
        "".join(
            '<span class="catalogue__badge">%s</span>' % html.escape(str(flag))
            for flag in (product.get("type_flags") or [])
        ) or '<span class="catalogue__badge">Lighting</span>',
        html.escape(product.get("description") or "Kineto LED lighting for modern spaces."),
        whatsapp,
        PRICE_LIST_URL,
        dl_rows,
        sibling_rows or '<span class="catalogue__meta-item">No sibling products found.</span>',
        html.escape(category),
        related_cards or '<span class="catalogue__meta-item">No related products found.</span>',
    )
        product_jsonld = json.dumps({
            "@context": "https://schema.org",
            "@type": "Product",
            "name": name,
            "image": [img for img in [variant.get("image") for variant in variants] if img],
            "sku": product_code,
            "brand": {"@type": "Brand", "name": "Kineto"},
            "description": product.get("description") or "Kineto LED lighting product.",
        }, ensure_ascii=False)
        canonical_url = SITE_URL + "/explore/lighting/%s/" % slug
        write("explore/lighting/%s/index.html" % slug, page(
            "%s &mdash; Kineto India" % name,
            product.get("description") or "Kineto LED lighting product.",
            body,
            active="/explore/",
            canonical=canonical_url,
            jsonld=product_jsonld,
            robots=NOINDEX,
        ))


def build_sitemap():
    entries = [
        "/",
        "/explore/",
        "/explore/lighting/",
        "/connect/",
        "/solutions/",
        "/why-kineto/",
        "/future/",
    ]
    for product in load_catalogue():
        entries.append("/explore/lighting/%s/" % product.get("slug"))
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
%s
</urlset>
""" % "\n".join(
        '  <url><loc>%s%s</loc></url>' % (SITE_URL, path)
        for path in dict.fromkeys(entries)
    )
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)


def write_redirects(products):
    rows = []
    seen = set()
    for product in products:
        old = product.get("old_href")
        if old:
            base = "/" + old
            dest = "/explore/lighting/%s/" % product.get("slug")
            for candidate in [base, base.replace(".php", "")]:
                if candidate and candidate not in seen:
                    rows.append((candidate, dest))
                    seen.add(candidate)
            for alias in product.get("aliases") or []:
                candidate = "/" + alias
                if candidate and candidate not in seen:
                    rows.append((candidate, dest))
                    seen.add(candidate)
        if product.get("slug"):
            candidate = "/explore/lighting/%s" % product.get("slug")
            if candidate not in seen:
                rows.append((candidate, "/explore/lighting/%s/" % product.get("slug")))
                seen.add(candidate)
    rows.append(("/led-lights", "/explore/lighting/"))
    rows.append(("/led-lights/", "/explore/lighting/"))

    csv_path = os.path.join(ROOT, "_dev", "redirects.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["old_url", "new_url"])
        for old, new in rows:
            if old and new:
                writer.writerow([old, new])

    htaccess = [
        "# Generated by build.py",
        "RewriteEngine On",
    ]
    for old, new in rows:
        if old.startswith("/"):
            htaccess.append("RewriteRule ^%s$ %s [R=301,L]" % (old.lstrip("/"), new))
    with open(os.path.join(ROOT, "_dev", "redirects.htaccess"), "w", encoding="utf-8") as f:
        f.write("\n".join(htaccess) + "\n")


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------

def build_home():
    words = ["Lights.", "Fans.", "Cities.", "Factories.", "Homes.", "Solar panels."]

    word_items = "\n".join(
        '      <div class="reveal" data-delay="%d"><span class="display-md">%s</span></div>'
        % (200 + i * 180, w) for i, w in enumerate(words)
    )

    pairs = "\n".join(
        '      <div class="reveal pair" data-delay="%d">'
        '<span class="display-lg pair__lead">%s</span>'
        '<span class="display-lg">%s</span></div>' % (i * 150, lead, punch)
        for i, (lead, punch) in enumerate(
            [("Don&rsquo;t just connect.", "Perform."), ("Don&rsquo;t just power.", "Progress.")])
    )

    sel_btns = "\n".join(
        '          <li><button type="button" class="selector__btn" data-selector-btn="%s" '
        'aria-selected="%s"><span class="display-md">%s</span>'
        '<span class="selector__tick"></span></button></li>'
        % (key, "true" if i == 0 else "false", label)
        for i, (key, label, _, _, _) in enumerate(SOLUTIONS)
    )

    sel_panels = []
    for i, (key, _, title, line, items) in enumerate(SOLUTIONS):
        lis = "\n".join("            <li>%s</li>" % it for it in items)
        sel_panels.append(
            '        <div class="selector__panel" data-selector-panel="%s"%s>\n'
            '          <p class="eyebrow">%s</p>\n'
            '          <p class="display-sm mt-3">%s</p>\n'
            '          <ul class="ticked mt-8">\n%s\n          </ul>\n'
            '          <a href="/solutions/" class="link link--spark label mt-10">See the full solution &rarr;</a>\n'
            '        </div>' % (key, "" if i == 0 else " hidden", title, line, lis)
        )

    worlds = list(CATEGORIES) + [dict(SOLAR, href="/future/", plain="Solar")]
    uni_rows, uni_shots = [], []
    for c in worlds:
        href = c.get("href", "/explore/%s/" % c.get("slug", ""))
        uni_rows.append(
            '          <li><a href="%s" class="universe__row" data-universe-row="%s">\n'
            '            <span class="universe__tick"></span>\n'
            '            <span class="label universe__num">%s</span>\n'
            '            <span>\n'
            '              <span class="display-md universe__name">%s</span>\n'
            '              <span class="label mt-3 text-%s" style="display:block">%s</span>\n'
            '            </span>\n'
            '          </a></li>' % (href, c["num"], c["num"], c["name"], c["tone"], c["statement"])
        )
        uni_shots.append(
            '          <img src="/assets/%s" alt="%s" width="1280" height="800" loading="lazy" '
            'class="img-dim%s" data-universe-shot="%s">'
            % (c["image"], c["plain"], " is-on" if c["num"] == "01" else "", c["num"])
        )

    proof_cards = "\n".join(
        '      <div class="reveal" data-delay="%d">\n'
        '        <div class="proof__card">\n'
        '          <img src="/assets/%s" alt="%s &mdash; %s" width="1280" height="800" loading="lazy" class="img-dim">\n'
        '          <div class="proof__caption">\n'
        '            <p class="eyebrow">%s</p>\n'
        '            <p class="display-sm mt-3">%s</p>\n'
        '          </div>\n'
        '        </div>\n'
        '      </div>' % (i * 80, img, title, line, title, line)
        for i, (_, title, line, img) in enumerate(PROOF)
    )

    story_cards = "\n".join(
        '      <div class="reveal story-card" data-delay="%d">\n'
        '        <span class="spark-dot mb-8" style="display:block"></span>\n'
        '        <blockquote class="display-sm normal-case">&ldquo;%s&rdquo;</blockquote>\n'
        '        <p class="label mt-8">&mdash; %s, %s</p>\n'
        '      </div>' % (i * 100, quote, who, where)
        for i, (quote, who, where) in enumerate(STORIES)
    )

    marquee = "".join(
        '<span class="display-md">%s<span class="dot"></span></span>' % c
        for c in CITIES * 2
    )

    audience = "\n".join(
        '        <li><a href="%s"><span class="label">%s</span>'
        '<span class="display-sm">%s &rarr;</span></a></li>' % (href, who, action)
        for who, action, href in AUDIENCES
    )

    body = """    <!-- Hero -->
    <section class="hero">
      <span class="hero__spark spark-dot"></span>
      <span class="hero__wire"></span>
      <div class="mt-10">
        <h1 class="hero__text display-xl">Power is not a number.</h1>
        <p class="hero__text--2 display-md mt-6 body">It&rsquo;s possibility.</p>
      </div>
      <span class="hero__scroll hero__text--2 label">Scroll</span>
    </section>

    <!-- 01 -->
    <section class="section">
%s
      <div class="reveal">
        <h2 class="display-lg">It&rsquo;s what makes<br>everything move.</h2>
      </div>
      <div class="wordlist">
%s
      </div>
    </section>

    <!-- 02 -->
    <section class="section section--tall">
      <div style="width:100%%">
%s
        <div class="reveal" data-delay="100">
          <h2 class="display-lg">When power stops,<br>life pauses.</h2>
        </div>
        <div class="reveal mt-10" data-delay="250">
          <p class="body-lg">A hospital. A classroom. A late shift on a factory floor. Everything that matters runs on a connection that must not fail.</p>
        </div>
      </div>
    </section>

    <!-- 03 -->
    <section class="section">
%s
      <div class="pairs">
%s
      </div>
    </section>

    <!-- 04 -->
    <section class="section bordered" data-selector>
%s
      <div class="reveal">
        <h2 class="display-lg">What are you looking to power?</h2>
      </div>
      <div class="selector">
        <ul>
%s
        </ul>
%s
      </div>
    </section>

    <!-- 05 -->
    <section class="section bordered" data-universe>
%s
      <div class="universe">
        <div class="universe__list">
          <span class="universe__spine"><span class="energy-line"></span></span>
          <ul>
%s
          </ul>
        </div>
        <div class="universe__stage">
%s
        </div>
      </div>
    </section>

    <!-- 06 -->
    <section class="section bordered" style="padding-inline:0">
      <div style="padding-inline:var(--gutter)">
%s
        <div class="reveal">
          <h2 class="display-lg">Engineered for<br>high performance.</h2>
        </div>
      </div>
      <div class="proof">
%s
      </div>
      <div class="mt-10" style="padding-inline:var(--gutter)">
        <a href="/why-kineto/" class="link link--spark label">See the proof &rarr;</a>
      </div>
    </section>

    <!-- 07 -->
    <section class="section bordered">
%s
      <div class="reveal">
        <h2 class="display-lg">Real connections.<br>Real stories.</h2>
      </div>
      <div class="hairgrid cols-2 mt-16">
%s
      </div>
    </section>

    <!-- 08 -->
    <section class="section bordered">
%s
      <div class="reveal">
        <h2 class="display-lg">Connected across India.</h2>
      </div>
      <div class="marquee-wrap">
        <span class="energy-line-x"></span>
        <div class="marquee" aria-hidden="true">%s</div>
        <p class="visually-hidden">Kineto is present in %s.</p>
      </div>
      <div class="mt-16">
        <p class="eyebrow mb-6">What brings you here?</p>
        <ul class="hairgrid cols-sm-2 cols-lg-3 audience">
%s
        </ul>
      </div>
    </section>

    <!-- 09 -->
    <section class="band">
      <img src="/assets/cat-solar.jpg" alt="Solar panels on a modern Indian rooftop at golden hour" width="1280" height="800" loading="lazy" class="band__img img-dim">
      <span class="band__scrim"></span>
      <div class="band__body">
        <div class="reveal section-head">
          <span class="label">09</span>
          <span class="rule rule-sun"></span>
          <span class="eyebrow text-sun">Kineto Solar</span>
        </div>
        <div class="reveal" data-delay="100">
          <h2 class="display-xl">The future runs<br>on electricity.</h2>
        </div>
        <div class="reveal mt-10" data-delay="250">
          <a href="/future/" class="link link--sun label">Don&rsquo;t wait for the future. Power it &rarr;</a>
        </div>
      </div>
    </section>

    <!-- 10 -->
    <section class="section section--deep">
%s
      <div class="reveal" data-delay="100">
        <h2 class="display-xl">High performance.<br><span class="text-spark">Every connection.</span></h2>
      </div>
    </section>
""" % (
        section_head("01"),
        word_items,
        section_head("02"),
        section_head("03", "Every connection matters"),
        pairs,
        section_head("04", "Explore what we power"),
        sel_btns,
        "\n".join(sel_panels),
        section_head("05", "The Kineto universe"),
        "\n".join(uni_rows),
        "\n".join(uni_shots),
        section_head("06", "Why Kineto"),
        proof_cards,
        section_head("07", "Real Kineto"),
        story_cards,
        section_head("08", "Network"),
        marquee,
        ", ".join(CITIES),
        audience,
        section_head("10", None, "rule", dot=True),
    )

    write("index.html", page(
        "Kineto India &mdash; High Performance. Every Connection.",
        "Kineto is a modern Indian electrical and energy brand: wires &amp; cables, lighting, switchgear, fans and solar, engineered for high performance.",
        body, active="/"))


# ---------------------------------------------------------------------------
# Explore index
# ---------------------------------------------------------------------------

def build_explore():
    rows = []
    for i, c in enumerate(CATEGORIES):
        rows.append(
            '      <li>\n'
            '        <a href="/explore/%s/" class="world">\n'
            '          <span class="label">%s</span>\n'
            '          <span>\n'
            '            <span class="display-lg world__name">%s</span>\n'
            '            <span class="label mt-3 text-%s" style="display:block">%s</span>\n'
            '          </span>\n'
            '          <span class="world__media">\n'
            '            <img src="/assets/%s" alt="%s" width="1280" height="800" loading="%s" class="img-dim">\n'
            '          </span>\n'
            '        </a>\n'
            '      </li>' % (c["slug"], c["num"], c["name"], c["tone"], c["statement"],
                             c["image"], c["plain"], "eager" if i == 0 else "lazy")
        )

    rows.append(
        '      <li>\n'
        '        <a href="/future/" class="world world--sun">\n'
        '          <span class="label">%s</span>\n'
        '          <span>\n'
        '            <span class="display-lg world__name">%s</span>\n'
        '            <span class="label mt-3 text-sun" style="display:block">%s</span>\n'
        '          </span>\n'
        '          <span class="world__media">\n'
        '            <img src="/assets/%s" alt="Kineto Solar" width="1280" height="800" loading="lazy" class="img-dim">\n'
        '          </span>\n'
        '        </a>\n'
        '      </li>' % (SOLAR["num"], SOLAR["name"], SOLAR["statement"], SOLAR["image"])
    )

    body = """    <section class="section section--top">
      <div class="reveal">
        <p class="eyebrow mb-6">02 &middot; Explore</p>
        <h1 class="display-xl">The Kineto universe.</h1>
      </div>
      <div class="reveal mt-10" data-delay="200">
        <p class="body-lg">Five worlds. One line of energy running through all of them.</p>
      </div>
    </section>

    <ul class="worlds">
%s
    </ul>
""" % "\n".join(rows)

    write("explore/index.html", page(
        "Explore Products &amp; Technology &mdash; Kineto India",
        "Wires &amp; cables, lighting, switchgear, fans and solar. Explore the Kineto universe of high-performance electrical products.",
        body, active="/explore/"))


# ---------------------------------------------------------------------------
# Category pages
# ---------------------------------------------------------------------------

def build_categories():
    products = load_catalogue()
    for i, c in enumerate(CATEGORIES):
        if c["slug"] == "lighting":
            build_catalogue(c, products)
            continue

        nxt = CATEGORIES[(i + 1) % len(CATEGORIES)]

        chapters = "\n".join(
            '    <section class="chapter">\n'
            '      <div class="chapter__grid">\n'
            '        <div class="reveal"><span class="label">%02d / %02d</span></div>\n'
            '        <div>\n'
            '          <div class="reveal"><h2 class="display-lg">%s</h2></div>\n'
            '          <div class="reveal mt-8" data-delay="200"><p class="body-lg">%s</p></div>\n'
            '        </div>\n'
            '      </div>\n'
            '    </section>' % (n + 1, len(c["story"]), title, text)
            for n, (title, text) in enumerate(c["story"])
        )

        tech = "\n".join(
            '        <div class="reveal tech-card" data-delay="%d">\n'
            '          <span class="tech-card__rule rule-%s"></span>\n'
            '          <h3 class="display-sm">%s</h3>\n'
            '          <p class="body mt-4">%s</p>\n'
            '        </div>' % (n * 100, c["tone"], title, text)
            for n, (title, text) in enumerate(c["tech"])
        )

        rng = "\n".join(
            '        <div class="reveal" data-delay="%d">\n'
            '          <span class="display-lg">%s</span>\n'
            '          %s\n'
            '        </div>' % (
                n * 120, name,
                '<span class="range__sep rule-%s"></span>' % c["tone"]
                if n < len(c["range"]) - 1 else "")
            for n, name in enumerate(c["range"])
        )

        body = """    <section class="hero-page">
      <img src="/assets/%s" alt="%s" width="1280" height="800" class="img-dim hero-page__img--spin">
      <span class="hero-page__scrim"></span>
      <div class="hero-page__body">
        <p class="eyebrow mb-6">%s &middot; %s</p>
        <h1 class="display-xl">%s</h1>
        <p class="label mt-8 text-%s">%s</p>
      </div>
    </section>

%s

    <section class="section bordered">
      <div class="reveal">
        <p class="eyebrow mb-6">Technology</p>
        <h2 class="display-md">Built into every unit.</h2>
      </div>
      <div class="hairgrid cols-md-3 mt-14">
%s
      </div>
    </section>

    <section class="section bordered">
      <div class="reveal"><p class="eyebrow mb-6">The range</p></div>
      <div class="range">
%s
      </div>
      <div class="reveal link-row mt-16" data-delay="300">
        <a href="/connect/#dealer" class="link link--spark label">Find a dealer &rarr;</a>
        <a href="/connect/#contact" class="link label">Request the catalogue &rarr;</a>
      </div>
    </section>

    <a href="/explore/%s/" class="next-world">
      <span class="label">Next world &middot; %s</span>
      <span class="display-lg next-world__name">%s &rarr;</span>
    </a>
""" % (c["image"], c["plain"], c["num"], c["name"], c["statement"], c["tone"],
       c["personality"], chapters, tech, rng, nxt["slug"], nxt["num"], nxt["name"])

        write("explore/%s/index.html" % c["slug"], page(
            "%s &mdash; %s | Kineto India" % (c["name"], c["statement"]),
            c["meta"], body, active="/explore/"))

    build_product_pages(products)
    build_sitemap()
    write_redirects(products)


# ---------------------------------------------------------------------------
# Solutions
# ---------------------------------------------------------------------------

def build_solutions():
    blocks = []
    for i, (key, _, title, line, items) in enumerate(SOLUTIONS):
        lis = "\n".join("            <li>%s</li>" % it for it in items)
        primary = ("/future/", "Calculate savings &rarr;") if key == "future" \
            else ("/explore/", "Explore the products &rarr;")
        blocks.append(
            '    <section class="solve" id="%s">\n'
            '      <div>\n'
            '        <div class="reveal">\n'
            '          <span class="label">0%d</span>\n'
            '          <h2 class="display-lg mt-4">%s</h2>\n'
            '        </div>\n'
            '        <div class="reveal mt-6" data-delay="150"><p class="body-lg">%s</p></div>\n'
            '      </div>\n'
            '      <div>\n'
            '        <div class="reveal" data-delay="200">\n'
            '          <p class="eyebrow mb-6">Kineto recommends</p>\n'
            '          <ul class="solve__list">\n%s\n          </ul>\n'
            '          <div class="link-row">\n'
            '            <a href="%s" class="link link--spark label">%s</a>\n'
            '            <a href="/connect/#dealer" class="link label">Talk to a dealer &rarr;</a>\n'
            '          </div>\n'
            '        </div>\n'
            '      </div>\n'
            '    </section>' % (key, i + 1, title, line, lis, primary[0], primary[1])
        )

    body = """    <section class="section section--top">
      <div class="reveal">
        <p class="eyebrow mb-6">03 &middot; Solve</p>
        <h1 class="display-xl">What are you looking to power?</h1>
      </div>
      <div class="reveal mt-10" data-delay="200">
        <p class="body-lg">You don&rsquo;t think in product hierarchies. Neither do we. Start with what you need.</p>
      </div>
    </section>

%s
""" % "\n\n".join(blocks)

    write("solutions/index.html", page(
        "Solutions for Homes, Businesses &amp; Industry &mdash; Kineto India",
        "What are you looking to power? Kineto recommends the right wires, lighting, fans, switchgear and solar for your home, business, industry or future.",
        body, active="/solutions/"))


# ---------------------------------------------------------------------------
# Why Kineto
# ---------------------------------------------------------------------------

def build_why():
    panels = "\n".join(
        '    <section class="proof-panel">\n'
        '      <img src="/assets/%s" alt="%s &mdash; %s" width="1280" height="800" loading="%s" class="img-dim">\n'
        '      <span class="proof-panel__scrim"></span>\n'
        '      <div class="proof-panel__body">\n'
        '        <div class="reveal">\n'
        '          <span class="eyebrow">0%d &middot; %s</span>\n'
        '          <h2 class="display-lg mt-4">%s</h2>\n'
        '        </div>\n'
        '      </div>\n'
        '    </section>' % (img, title, line, "eager" if i == 0 else "lazy", i + 1, title, line)
        for i, (_, title, line, img) in enumerate(PROOF)
    )

    cards = "\n".join(
        '        <div class="reveal story-card" data-delay="%d">\n'
        '          <span class="spark-dot mb-8" style="display:block"></span>\n'
        '          <blockquote class="display-sm normal-case">&ldquo;%s&rdquo;</blockquote>\n'
        '          <p class="label mt-8">&mdash; %s, %s</p>\n'
        '        </div>' % (i * 100, quote, who, where)
        for i, (quote, who, where) in enumerate(STORIES)
    )

    body = """    <section class="section section--top">
      <div class="reveal">
        <p class="eyebrow mb-6">01 &middot; Believe</p>
        <h1 class="display-xl">We don&rsquo;t say trusted. We show it.</h1>
      </div>
      <div class="reveal mt-10" data-delay="200">
        <p class="body-lg">Kineto designs, tools, builds and tests in-house. That isn&rsquo;t a claim on a page. It is a factory floor, a test rig and a person whose name stands behind the product.</p>
      </div>
    </section>

%s

    <section class="section bordered" id="stories">
      <div class="reveal">
        <p class="eyebrow mb-6">Real Kineto</p>
        <h2 class="display-lg">Real connections.<br>Real stories.</h2>
      </div>
      <div class="hairgrid cols-2 mt-16">
%s
      </div>
      <div class="reveal mt-12">
        <a href="/connect/" class="link link--spark label">Become part of the network &rarr;</a>
      </div>
    </section>
""" % (panels, cards)

    write("why-kineto/index.html", page(
        "Why Kineto &mdash; Built with Precision, Tested for Performance",
        "Kineto&rsquo;s story in proof, not promises: in-house tooling, design, testing and R&amp;D, and the real electricians, retailers and engineers behind every connection.",
        body, active="/why-kineto/"))


# ---------------------------------------------------------------------------
# Future / Solar
# ---------------------------------------------------------------------------

def build_future():
    pillars = "\n".join(
        '      <div class="reveal pillar" data-delay="%d">\n'
        '        <span class="pillar__rule"></span>\n'
        '        <h3 class="display-sm">%s</h3>\n'
        '        <p class="body mt-4">%s</p>\n'
        '      </div>' % (i * 100, title, text)
        for i, (title, text) in enumerate(PILLARS)
    )

    body = """    <section class="hero-page">
      <img src="/assets/cat-solar.jpg" alt="Solar panels on a modern Indian rooftop at golden hour" width="1280" height="800" class="hero-page__img">
      <span class="hero-page__scrim hero-page__scrim--solar"></span>
      <div class="hero-page__body">
        <p class="eyebrow mb-6 text-sun">05 &middot; Future &middot; Kineto Solar</p>
        <h1 class="display-xl">Don&rsquo;t wait for<br>the future.<br><span class="text-sun">Power it.</span></h1>
      </div>
    </section>

    <section class="section bordered" style="display:grid;gap:2.5rem">
      <div class="reveal"><h2 class="display-lg">Own the energy you use.</h2></div>
      <div class="reveal" data-delay="150">
        <p class="body-lg">Kineto Solar keeps its own optimistic identity inside the Kineto ecosystem: the same engineering discipline, pointed at the sun. Rooftop systems, inverters and storage for homes, businesses and industry, backed by the network you already trust for what&rsquo;s behind your walls.</p>
      </div>
    </section>

    <section class="section bordered" id="calculator" data-calc>
      <div class="reveal">
        <p class="eyebrow mb-6 text-sun">Calculate savings</p>
        <h2 class="display-lg">What could your roof earn?</h2>
      </div>

      <div class="calc">
        <div>
          <div class="calc__modes">
            <button type="button" class="calc__mode label" data-calc-mode="home" aria-pressed="true">My home</button>
            <button type="button" class="calc__mode label" data-calc-mode="business" aria-pressed="false">My business</button>
          </div>
          <label class="label" for="bill" style="display:block">Monthly electricity bill</label>
          <p class="display-lg calc__out" data-calc-billout>&#8377;4,000</p>
          <input id="bill" class="calc__slider" type="range" min="1000" max="100000" step="500" value="4000" data-calc-bill>
        </div>

        <dl class="hairgrid" style="grid-template-columns:repeat(2,1fr)">
          <div class="calc__cell">
            <dt class="label">Suggested system</dt>
            <dd class="display-md mt-3" data-calc-size>4.2 kW</dd>
          </div>
          <div class="calc__cell">
            <dt class="label">Estimated yearly saving</dt>
            <dd class="display-md mt-3" data-calc-saving>&#8377;40,800</dd>
          </div>
          <div class="calc__cell">
            <dt class="label">Indicative cost</dt>
            <dd class="display-md mt-3" data-calc-cost>&#8377;2,31,000</dd>
          </div>
          <div class="calc__cell">
            <dt class="label">Payback</dt>
            <dd class="display-md mt-3" data-calc-payback>~5.7 years</dd>
          </div>
        </dl>
      </div>

      <p class="calc__note">Planning estimate only. Actual savings depend on your roof, location, tariff and subsidies. A Kineto Solar partner will size it precisely.</p>

      <div class="reveal mt-10">
        <a href="/connect/#contact" class="link link--sun label">Get a real quote &rarr;</a>
      </div>
    </section>

    <section class="hairgrid cols-md-3 bordered">
%s
    </section>
""" % pillars

    write("future/index.html", page(
        "Kineto Solar &mdash; Don&rsquo;t Wait for the Future. Power It.",
        "Kineto Solar: rooftop solar for Indian homes, businesses and industry. Estimate your savings and own the energy you use.",
        body, active="/future/"))


# ---------------------------------------------------------------------------
# Connect
# ---------------------------------------------------------------------------

def build_connect():
    routes = [
        ("dealer", "01", "Consumers &amp; retailers", "Find a dealer or distributor.",
         "Tell us your city on WhatsApp and we&rsquo;ll connect you with the nearest Kineto counter, today.",
         "Find on WhatsApp &rarr;", WHATSAPP, True, None),
        ("kineward", "02", "Electricians", "Join Kineward.",
         "Kineward is Kineto&rsquo;s loyalty ecosystem for electricians: earn on every installation, unlock rewards and be recognised for the name you put behind your work.",
         "Register interest &rarr;", "mailto:%s?subject=Kineward" % EMAIL, False,
         ("Hear from electricians &rarr;", "/why-kineto/#stories")),
        ("partner", "03", "Distributors &amp; builders", "Partner with Kineto.",
         "Distribution partnerships, project supply and bulk enquiries for builders and contractors. One conversation to start.",
         "Project enquiry &rarr;", "mailto:%s?subject=Partnership%%20enquiry" % EMAIL, False, None),
    ]

    blocks = []
    for rid, num, who, title, text, cta, href, external, secondary in routes:
        extra = ('\n        <div class="mt-4"><a href="%s" class="link label">%s</a></div>'
                 % (secondary[1], secondary[0])) if secondary else ""
        blocks.append(
            '    <section class="route" id="%s">\n'
            '      <div class="reveal"><span class="label">%s</span></div>\n'
            '      <div class="reveal" data-delay="100">\n'
            '        <span class="eyebrow">%s</span>\n'
            '        <h2 class="display-lg mt-4">%s</h2>\n'
            '      </div>\n'
            '      <div class="reveal route__body" data-delay="200">\n'
            '        <p class="body-lg">%s</p>\n'
            '        <a href="%s"%s class="link link--spark label mt-8">%s</a>%s\n'
            '      </div>\n'
            '    </section>' % (rid, num, who, title, text, href,
                                ' target="_blank" rel="noreferrer"' if external else "",
                                cta, extra)
        )

    contacts = [
        ("Call", PHONE_DISPLAY, "tel:%s" % PHONE),
        ("WhatsApp", "Chat with Kineto", WHATSAPP),
        ("Email", EMAIL, "mailto:%s" % EMAIL),
    ]

    cards = "\n".join(
        '        <a href="%s" class="contact-card">\n'
        '          <span class="label">%s</span>\n'
        '          <span class="display-sm contact-card__value">%s</span>\n'
        '        </a>' % (href, label, value)
        for label, value, href in contacts
    )

    body = """    <section class="section section--top">
      <div class="reveal">
        <p class="eyebrow mb-6">04 &middot; Connect</p>
        <h1 class="display-xl">Every connection starts with one.</h1>
      </div>
    </section>

%s

    <section class="section bordered" id="contact">
      <div class="reveal">
        <p class="eyebrow mb-6">Contact</p>
        <h2 class="display-lg">One click. No forms.</h2>
      </div>
      <div class="hairgrid cols-3 mt-14">
%s
      </div>
    </section>
""" % ("\n\n".join(blocks), cards)

    write("connect/index.html", page(
        "Connect &mdash; Dealers, Electricians, Kineward &amp; Partners | Kineto India",
        "Find a Kineto dealer or distributor, join the Kineward rewards ecosystem for electricians, partner with Kineto, or send a project enquiry.",
        body, active="/connect/"))


# ---------------------------------------------------------------------------
# 404
# ---------------------------------------------------------------------------

def build_404():
    body = """    <section class="notfound">
      <div>
        <p class="eyebrow mb-6">404</p>
        <h1 class="display-lg">This line goes nowhere.</h1>
        <div class="mt-10">
          <a href="/" class="link link--spark label">Back to Kineto &rarr;</a>
        </div>
      </div>
    </section>
"""
    write("404.html", page("Page not found &mdash; Kineto India",
                           "This line goes nowhere. Head back to Kineto India.", body))


if __name__ == "__main__":
    print("Building Kineto India…")
    build_home()
    build_explore()
    build_categories()
    build_solutions()
    build_why()
    build_future()
    build_connect()
    build_404()
    print("Done.")
