"""Builds the publications carousel used on the homepage (index.qmd)."""
import base64
from pathlib import Path

import yaml
from IPython.display import HTML

PUB_DIR = Path(__file__).resolve().parent
ICON_DIR = PUB_DIR / "icons"

SCHOLAR_URL = "https://scholar.google.com/citations?user=ppZtojkAAAAJ&hl=en"
INSPIRE_URL = "https://inspirehep.net/authors/2750519"

# Predefined (background, text) colours per keyword, case-insensitive. Red/crimson is
# reserved for the "Preprint" link button, so no tag colour (including fallbacks) uses it.
# Any tag not listed here is assigned a stable colour from FALLBACK_TAG_COLORS based on its
# text, so new keywords in publications.yml never need a matching code change.
TAG_COLORS = {
    "cosmology": ("#e6f2ea", "#2f6f4f"),
    "inflation": ("#f1eaf7", "#7a5c9e"),
    "numerical relativity": ("#faf1e6", "#b5651d"),
    "stochastic methods": ("#e6f4f6", "#1f7a8c"),
    "machine learning": ("#eef0fb", "#4b3f96"),
    "nlp": ("#fdf3e0", "#a9790a"),
    "fairness": ("#f3e8f9", "#8e44ad"),
    "quantum crystallography": ("#e8f2fa", "#2874a6"),
}
FALLBACK_TAG_COLORS = [
    ("#e8f2fa", "#4a7fa5"),
    ("#eef0f5", "#556080"),
    ("#f0f5e8", "#5a7d2a"),
    ("#e6f7f7", "#12777a"),
]

# Fixed text + CSS modifier class per link type.
LINK_STYLES = {
    "preprint": ("Preprint", "pub-link-preprint"),
    "article": ("Article", "pub-link-article"),
    "thesis": ("Thesis", "pub-link-thesis"),
}


def _tag_colors(tag):
    key = tag.strip().lower()
    if key in TAG_COLORS:
        return TAG_COLORS[key]
    return FALLBACK_TAG_COLORS[sum(map(ord, key)) % len(FALLBACK_TAG_COLORS)]


def _encode_image(path):
    ext = path.suffix.lstrip(".").lower()
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    data = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/{mime};base64,{data}"


def _card_html(pub):
    icon_path = ICON_DIR / pub["icon"] if pub.get("icon") else None
    if icon_path and icon_path.exists():
        src = _encode_image(icon_path)
        image_html = f'<img class="carousel-card-image" src="{src}" alt="">'
    else:
        image_html = '<div class="carousel-card-image-placeholder">Visualisation coming soon</div>'

    meta_parts = []
    if pub.get("authors"):
        meta_parts.append(", ".join(pub["authors"]))
    if pub.get("venue"):
        meta_parts.append(pub["venue"])
    if pub.get("date"):
        meta_parts.append(pub["date"])
    meta_html = " · ".join(meta_parts)

    if pub.get("description"):
        desc_html = f'<div class="carousel-card-desc">{pub["description"]}</div>'
    else:
        desc_html = '<div class="carousel-card-desc-placeholder">Description coming soon</div>'

    links_html = "".join(
        f'<a class="pub-link {css_class}" href="{link["url"]}" target="_blank" rel="noopener">{text}</a>'
        for link in pub.get("links", [])
        for text, css_class in [LINK_STYLES.get(link.get("type"), ("Link", "pub-link-article"))]
    )

    tags_html = "".join(
        f'<span class="pub-tag" style="background-color:{bg};color:{fg};">{tag}</span>'
        for tag in pub.get("tags", [])
        for bg, fg in [_tag_colors(tag)]
    )

    return f"""
    <div class="carousel-card">
      {image_html}
      <div class="carousel-card-body">
        <div class="carousel-card-title">{pub["title"]}</div>
        <div class="carousel-card-meta">{meta_html}</div>
        {desc_html}
        <div class="pub-links">{links_html}</div>
        <div class="pub-tags">{tags_html}</div>
      </div>
    </div>"""


def build_publications():
    data = yaml.safe_load((PUB_DIR / "publications.yml").read_text(encoding="utf-8")) or {}
    publications = data.get("publications") or []

    if not publications:
        return HTML(f"""
        <p><em>Publication cards coming soon — meanwhile see my
        <a href="{SCHOLAR_URL}" target="_blank" rel="noopener">Google Scholar</a> or
        <a href="{INSPIRE_URL}" target="_blank" rel="noopener">INSPIRE-HEP</a> profile.</em></p>
        """)

    cards = "".join(_card_html(pub) for pub in publications)
    html = f"""
    <div class="carousel">
      <button class="carousel-btn prev" onclick="carouselScroll(this,-1)" aria-label="Previous">&#8249;</button>
      <div class="carousel-track">
        {cards}
      </div>
      <button class="carousel-btn next" onclick="carouselScroll(this,1)" aria-label="Next">&#8250;</button>
    </div>"""
    return HTML(html)
