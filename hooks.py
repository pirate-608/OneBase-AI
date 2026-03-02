"""MkDocs hooks for post-build tasks."""

import shutil
from pathlib import Path


def on_post_build(config, **kwargs):
    """Copy sitemap.xml into every subdirectory of the built site so that
    mkdocs-material's navigation.instant can locate it from any page."""
    site_dir = Path(config["site_dir"])
    sitemap = site_dir / "sitemap.xml"
    sitemap_gz = site_dir / "sitemap.xml.gz"

    if not sitemap.exists():
        return

    for sub in site_dir.rglob("index.html"):
        target_dir = sub.parent
        if target_dir == site_dir:
            continue
        if not (target_dir / "sitemap.xml").exists():
            shutil.copy2(sitemap, target_dir / "sitemap.xml")
        if sitemap_gz.exists() and not (target_dir / "sitemap.xml.gz").exists():
            shutil.copy2(sitemap_gz, target_dir / "sitemap.xml.gz")
