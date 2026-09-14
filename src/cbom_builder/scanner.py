"""Match an inventory of OT protocol/identity components against the PQC crosswalk.

An inventory row describes one component a user has observed in their own environment.
Required field: `protocol`. Recommended: `component` (narrows the match when a protocol
has multiple crosswalk rows, e.g. OPC UA). Optional passthrough fields (`asset_id`,
`location`, `classical_algorithm_observed`, `key_bits_observed`, ...) are carried into the
finding unchanged so a report can be traced back to the asset it came from.

Matching is deliberately simple and explainable rather than fuzzy/ML matching, so every
match in a report is easy for the author or a reader to verify by eye against
data/processed/pqc_crosswalk.csv:

  1. If the inventory row names a `crosswalk_id` (e.g. "OT-006"), that row is used
     directly -- the precise way to avoid any ambiguity.
  2. Otherwise, `protocol` (and `component`, if given) are matched against the
     crosswalk by substring containment, punctuation-insensitive (commas, slashes and
     parentheses are ignored so "SAv6 (AMP)" and "SAv6, AMP" match the same way).
"""

import re

REQUIRED_INVENTORY_FIELDS = ("protocol",)

_PUNCT_RE = re.compile(r"[^a-z0-9 ]+")
_SPACE_RE = re.compile(r"\s+")


class InventoryError(ValueError):
    """Raised when an inventory row is missing a required field."""


def _norm(s):
    s = (s or "").strip().lower()
    s = _PUNCT_RE.sub(" ", s)
    return _SPACE_RE.sub(" ", s).strip()


def _match_rows(protocol, component, crosswalk):
    protocol_n = _norm(protocol)
    component_n = _norm(component)

    candidates = [r for r in crosswalk if protocol_n in _norm(r["protocol"])
                  or _norm(r["protocol"]) in protocol_n]
    if not candidates:
        return []
    if component_n:
        narrowed = [r for r in candidates if component_n in _norm(r["component"])
                    or _norm(r["component"]) in component_n]
        if narrowed:
            return narrowed
    return candidates


def scan_inventory(inventory_rows, crosswalk):
    """Match each inventory row against the crosswalk.

    Returns a list of findings, one per inventory row, each augmented with:
      - `matches`: list of crosswalk rows that matched (0, 1, or more)
      - `match_status`: "matched" | "ambiguous" (>1 match) | "unmatched"
    """
    findings = []
    for i, row in enumerate(inventory_rows):
        missing = [f for f in REQUIRED_INVENTORY_FIELDS if not row.get(f)]
        if missing:
            raise InventoryError(
                f"inventory row {i} is missing required field(s): {', '.join(missing)}"
            )
        explicit_id = row.get("crosswalk_id")
        if explicit_id:
            matched = [r for r in crosswalk if r["id"] == explicit_id]
            if not matched:
                raise InventoryError(
                    f"inventory row {i} names crosswalk_id {explicit_id!r}, which does "
                    f"not exist in the crosswalk"
                )
            matches = matched
        else:
            matches = _match_rows(row.get("protocol"), row.get("component"), crosswalk)
        status = "unmatched" if not matches else ("ambiguous" if len(matches) > 1 else "matched")
        findings.append({
            **row,
            "matches": matches,
            "match_status": status,
        })
    return findings
