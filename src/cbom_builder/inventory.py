"""Load a user's component inventory from CSV or JSON."""

import csv
import json
import os


def load_inventory(path):
    """Return the inventory as a list of dicts, from a .csv or .json file."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = data.get("components", data.get("items", []))
        return list(data)
    if ext == ".csv":
        with open(path, newline="", encoding="utf-8") as f:
            return [dict(row) for row in csv.DictReader(f)]
    raise ValueError(f"unsupported inventory file type: {path} (use .csv or .json)")
