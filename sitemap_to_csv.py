#!/usr/bin/env python3
"""
Download every link from a sitemap (including nested sitemap.xml targets) and write them to CSV.

Usage:
    python sitemap_to_csv.py https://paen.com/sitemap.xml --output ./paen-links.csv
"""

from __future__ import annotations

import argparse
import csv
import ssl
import sys
import urllib.request
from typing import Iterable, Set

from xml.etree import ElementTree as ET

XML_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
NS = {"sm": XML_NAMESPACE}


def fetch_xml(url: str, cert_file: str | None = None) -> bytes:
    """Retrieve the raw bytes of an XML document."""
    context = ssl.create_default_context()
    if cert_file:
        context = ssl.create_default_context(cafile=cert_file)

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        },
    )
    with urllib.request.urlopen(req, context=context) as response:
        return response.read()


def is_xml_link(url: str) -> bool:
    """Detect whether the link looks like a sitemap (ends with .xml)."""
    return url.lower().rstrip("/").endswith(".xml")


def parse_sitemap(url: str, seen_xml: Set[str], emit: Set[str], cert_file: str | None = None) -> None:
    """Recursively walk a sitemap, adding URL targets into the emit set."""
    if url in seen_xml:
        return
    seen_xml.add(url)

    data = fetch_xml(url, cert_file)
    root = ET.fromstring(data)
    tag = root.tag.split("}", 1)[-1]

    if tag == "sitemapindex":
        for sitemap in root.findall("sm:sitemap", NS):
            loc = sitemap.findtext("sm:loc", ".//", NS)
            if loc:
                parse_sitemap(loc.strip(), seen_xml, emit, cert_file=cert_file)
    elif tag == "urlset":
        for url_entry in root.findall("sm:url", NS):
            loc = url_entry.findtext("sm:loc")
            if not loc:
                continue
            loc = loc.strip()
            if is_xml_link(loc):
                parse_sitemap(loc, seen_xml, emit, cert_file=cert_file)
            else:
                emit.add(loc)
    else:
        raise ValueError(f"Unsupported sitemap root tag: {root.tag}")


def collect_urls(root_sitemap: str, cert_file: str | None = None) -> Set[str]:
    """Return every (non-XML) URL mentioned inside the sitemap hierarchy."""
    seen_xml: Set[str] = set()
    collected: Set[str] = set()
    parse_sitemap(root_sitemap, seen_xml, collected, cert_file=cert_file)
    return collected


def write_csv(urls: Iterable[str], path: str) -> None:
    """Write URLs to CSV with a single `url` column."""
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["url"])
        for url in sorted(urls):
            writer.writerow([url])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export sitemap URLs to CSV.")
    parser.add_argument("sitemap", help="URL of the root sitemap.")
    parser.add_argument(
        "-o",
        "--output",
        default="sitemap_urls.csv",
        help="Path to write CSV output (defaults to sitemap_urls.csv).",
    )
    parser.add_argument(
        "--cert-file",
        default=None,
        help="Optional CA bundle (defaults to system certificates).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        collected = collect_urls(args.sitemap, cert_file=args.cert_file)
    except Exception as err:  # pragma: no cover
        print(f"Failed to parse sitemap: {err}", file=sys.stderr)
        sys.exit(1)

    write_csv(collected, args.output)
    print(f"Wrote {len(collected)} unique URLs to {args.output}")


if __name__ == "__main__":
    main()

