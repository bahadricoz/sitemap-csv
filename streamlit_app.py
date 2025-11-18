"""
Streamlit interface for sitemap_to_csv.py

Users can supply any sitemap XML URL, then download all discovered URLs as CSV.
"""

from __future__ import annotations

import csv
import io

import certifi
import streamlit as st

from sitemap_to_csv import collect_urls

DEFAULT_SITEMAP = "https://paen.com/sitemap.xml"


def _build_csv(urls: set[str]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["url"])
    for url in sorted(urls):
        writer.writerow([url])
    return buffer.getvalue()


st.set_page_config(page_title="Sitemap to CSV", page_icon="🗺️")
st.title("Sitemap to CSV")
st.write("Enter any sitemap root URL (including sitemap index files) and download a CSV of every child link.")

with st.form("sitemap_form"):
    sitemap_url = st.text_input("Root sitemap URL", DEFAULT_SITEMAP)
    output_name = st.text_input("CSV file name", "sitemap_links.csv")
    use_certifi = st.checkbox("Use certifi CA bundle (recommended)", value=True)
    strip_domain = st.checkbox("Strip scheme+host (keep only path/query/fragment)", value=True)
    submitted = st.form_submit_button("Collect URLs")

if submitted:
    sitemap_url = sitemap_url.strip()
    if not sitemap_url:
        st.error("Please provide a sitemap URL.")
    else:
        cert_file = certifi.where() if use_certifi else None
        try:
            with st.spinner("Collecting URLs…"):
                urls = collect_urls(
                    sitemap_url,
                    cert_file=cert_file,
                    strip_domain=strip_domain,
                )
        except Exception as exc:
            st.error(f"Failed to collect URLs: {exc}")
        else:
            st.success(f"Discovered {len(urls)} URL(s)")
            st.download_button(
                "Download CSV",
                _build_csv(urls),
                file_name=output_name.strip() or "sitemap_links.csv",
                mime="text/csv",
            )
            if urls:
                st.divider()
                st.caption("Sample URLs")
                st.dataframe([[url] for url in sorted(urls)[:10]], columns=["url"])

