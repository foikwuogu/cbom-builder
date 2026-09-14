#!/usr/bin/env python3
"""Inject the crosswalk data and example inventory into web/index.html.

web/index_template.html is the source of truth for the page; this script never edits
markup, only substitutes the two data placeholders, so the built web/index.html is
always reproducible from the template plus data/processed/pqc_crosswalk.json.

Run: python code/02_build_web.py
"""

import csv
import json
import os

ROOT = os.path.join(os.path.dirname(__file__), "..")


def main():
    crosswalk_path = os.path.join(ROOT, "data", "processed", "pqc_crosswalk.json")
    inventory_path = os.path.join(ROOT, "tests", "fixtures", "sample_inventory.csv")
    template_path = os.path.join(ROOT, "web", "index_template.html")
    out_path = os.path.join(ROOT, "web", "index.html")

    with open(crosswalk_path, encoding="utf-8") as f:
        crosswalk = json.load(f)
    with open(inventory_path, encoding="utf-8") as f:
        example_csv = f.read()

    with open(template_path, encoding="utf-8") as f:
        html = f.read()

    html = html.replace("__CROSSWALK_JSON__", json.dumps(crosswalk))
    html = html.replace("__EXAMPLE_CSV__", json.dumps(example_csv))

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"wrote {out_path} ({len(crosswalk)} crosswalk rows embedded)")


if __name__ == "__main__":
    main()
