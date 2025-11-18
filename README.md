# Sitemap to CSV

Tooling to walk any sitemap (including nested `.xml` sitemaps) and export all discovered URLs as a CSV.

## CLI

Install dependencies (optionally using a virtualenv):

```bash
python3 -m pip install certifi
```

Run the root sitemap and point `SSL_CERT_FILE` at the `certifi` bundle to avoid macOS/CI SSL issues:

```bash
SSL_CERT_FILE=$(python3 -m certifi) python3 sitemap_to_csv.py https://paen.com/sitemap.xml --output paen-links.csv
```

You can optionally pass `--cert-file` instead of relying on the environment variable.

## Streamlit interface

1. Install the UI dependencies:

   ```bash
   python3 -m pip install -r requirements.txt
   ```

2. Run the Streamlit app locally:

   ```bash
   streamlit run streamlit_app.py
   ```

3. Enter a sitemap URL, tweak the CSV file name, and click **Collect URLs**. A download button appears when the crawl completes.

To publish a permanent link, deploy the repo to [Streamlit Community Cloud](https://streamlit.io/cloud) (or any Streamlit-compatible host) and set the command to `streamlit run streamlit_app.py`.

## GitHub Actions

The `.github/workflows/sitemap-to-csv.yml` workflow runs on push and manually (`workflow_dispatch`). It installs `certifi`, runs the collector, and uploads `paen-links.csv` as an artifact for download. You can trigger it from the Actions tab or share each run’s URL/artifact link with your team.

