#!/usr/bin/env python3
"""Check all three production builds before rclone sync. Standard library only."""
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DOMAINS = {"ru": "akimova.ru", "en": "akimova.pro", "zh": "akimova.asia"}
HTML_LANGUAGES = {"ru": "ru-RU", "en": "en-US", "zh": "zh-CN"}
HREFLANGS = {"ru": "ru", "en": "en", "zh": "zh-CN"}
ICONS = (
    "favicon.svg", "favicon.ico", "favicon-16x16.png", "favicon-32x32.png",
    "favicon-48x48.png", "favicon-96x96.png", "apple-touch-icon.png",
    "web-app-manifest-192x192.png", "web-app-manifest-512x512.png",
    "web-app-manifest-maskable-512x512.png",
)


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.elements = []
        self.in_head = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag == "head":
            self.in_head = True
        self.elements.append((tag, dict(attrs), self.in_head))

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False

    def links(self, relation):
        return [a for tag, a, head in self.elements
                if tag == "link" and head and relation in a.get("rel", "").split()]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check():
    pages = {}
    for language, domain in DOMAINS.items():
        directory = ROOT / "public" / domain
        for name in ("index.html", "about/index.html", "sitemap.xml", "robots.txt",
                     "site.webmanifest", *ICONS):
            path = directory / name
            require(path.is_file() and path.stat().st_size,
                    f"Missing or empty {path}. Run ./build.sh first.")
        manifest = json.loads((directory / "site.webmanifest").read_text())
        for icon in manifest["icons"]:
            require((directory / icon["src"].lstrip("/")).is_file(),
                    f"Missing manifest icon: {domain}{icon['src']}")

        # XML parsing also catches malformed or accidentally empty sitemaps.
        import xml.etree.ElementTree as ET
        sitemap = ET.parse(directory / "sitemap.xml")
        locations = {item.text for item in sitemap.findall(
            ".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")}
        require(locations and all(url.startswith(f"https://{domain}/") for url in locations),
                f"Incorrect sitemap domain for {domain}")
        require(f"Sitemap: https://{domain}/sitemap.xml" in (directory / "robots.txt").read_text(),
                f"Incorrect robots.txt sitemap for {domain}")

        pages[language] = {}
        for path in sorted(directory.rglob("*.html")):
            relative = path.relative_to(directory).as_posix()
            route = "/" + relative
            if route.endswith("index.html"):
                route = route[:-len("index.html")]
            document = Document(path.read_text())
            label = f"{domain}{route}"
            html = [a for tag, a, _ in document.elements if tag == "html"]
            require(len(html) == 1 and html[0].get("lang") == HTML_LANGUAGES[language],
                    f"Incorrect HTML language: {label}")
            canonical = document.links("canonical")
            require(len(canonical) == 1 and canonical[0].get("href") == f"https://{domain}{route}",
                    f"Incorrect canonical: {label}")
            descriptions = [a.get("content") for tag, a, head in document.elements
                            if tag == "meta" and head and a.get("name") == "description"]
            require(len(descriptions) == 1 and descriptions[0], f"Missing description: {label}")
            noindex = any(tag == "meta" and a.get("name") == "robots" and
                          "noindex" in a.get("content", "") for tag, a, _ in document.elements)
            alternates = document.links("alternate")
            alternate_list = [a for a in alternates if "hreflang" in a]
            alternate_map = {a["hreflang"]: a.get("href") for a in alternate_list}
            require(len(alternate_map) == len(alternate_list), f"Duplicate hreflang: {label}")
            if relative == "404.html" or noindex:
                require(noindex and not alternate_map, f"Invalid noindex metadata: {label}")
            else:
                require(f"https://{domain}{route}" in locations, f"Missing sitemap URL: {label}")
                pages[language][route] = (document, alternate_map)

            if language == "zh":
                require(any(tag == "meta" and attrs.get("name") == "author" and
                            attrs.get("content") == "Elizabeth Akimova"
                            for tag, attrs, _ in document.elements),
                        f"Incorrect Chinese-site author: {label}")
                require(any(tag == "a" and attrs.get("href") == "mailto:elizabeth@akimova.pro"
                            for tag, attrs, _ in document.elements),
                        f"Incorrect Chinese-site email: {label}")
                for tag, attrs, _ in document.elements:
                    if tag == "a" and "gallery-item" in attrs.get("class", "").split():
                        require(any("\u4e00" <= c <= "\u9fff" for c in attrs.get("title", "")),
                                f"Missing Chinese artwork caption: {label} {attrs.get('href')}")

            # Check local navigation and assets, including favicon/CSS/JS/image URLs.
            for tag, attrs, _ in document.elements:
                for attribute in ("src", "href"):
                    value = attrs.get(attribute, "")
                    url = urlsplit(value)
                    if not value or url.scheme or url.netloc or not url.path:
                        continue
                    target = (directory / unquote(url.path).lstrip("/") if url.path.startswith("/")
                              else path.parent / unquote(url.path))
                    require(target.is_file() or (target / "index.html").is_file(),
                            f"Broken local {attribute} in {label}: {value}")

    # Translation paths must match; do not silently advertise missing pages.
    for language in DOMAINS:
        require(pages["ru"].keys() == pages[language].keys(), f"RU/{language} page paths differ")
    for language, documents in pages.items():
        for route, (document, alternate_map) in documents.items():
            expected = {HREFLANGS[code]: f"https://{domain}{route}"
                        for code, domain in DOMAINS.items()}
            expected["x-default"] = expected["en"]
            require(alternate_map == expected, f"Incorrect hreflang: {language}{route}")
            for other in DOMAINS.keys() - {language}:
                require(any(tag == "a" and attrs.get("hreflang") == HREFLANGS[other] and
                            attrs.get("href") == expected[HREFLANGS[other]]
                            for tag, attrs, _ in document.elements),
                        f"Missing {other} language switch: {language}{route}")
    print(f"OK: {sum(map(len, pages.values()))} pages; canonical, hreflang, language switches, "
          "local links, icons, manifests, sitemaps and robots.txt.")


if __name__ == "__main__":
    try:
        check()
    except (ValueError, OSError, KeyError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
