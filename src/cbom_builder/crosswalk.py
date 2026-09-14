"""Load and query the PQC readiness crosswalk.

The crosswalk ships as package data (built by code/01_build_crosswalk.py from cited
public specifications -- see data/raw/PROVENANCE.txt) so the package works standalone
once installed, but a caller can also point at a newer or customized crosswalk file.
"""

import importlib.resources
import json
from pathlib import Path

_PACKAGE_DATA = "pqc_crosswalk.json"


def load_crosswalk(path=None):
    """Return the crosswalk as a list of dicts.

    Args:
        path: optional path to a crosswalk JSON file. If omitted, the crosswalk bundled
            with the package is used.
    """
    if path is not None:
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    data = importlib.resources.files("cbom_builder.data").joinpath(_PACKAGE_DATA)
    with importlib.resources.as_file(data) as p:
        return json.loads(Path(p).read_text(encoding="utf-8"))


def find_by_id(crosswalk, entry_id):
    """Return the crosswalk row with this id, or None."""
    for row in crosswalk:
        if row["id"] == entry_id:
            return row
    return None
