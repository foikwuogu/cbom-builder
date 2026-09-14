"""Build and write a CBOM report from scanner findings."""

import csv
import datetime
import json

from . import __version__

THREAT_ORDER = ["broken-by-shor", "weakened-by-grover", "no-crypto", "not-vulnerable"]


def build_report(findings):
    """Summarize findings into a CBOM report dict."""
    threat_counts = {t: 0 for t in THREAT_ORDER}
    unmatched = []
    ambiguous = []
    items = []

    for f in findings:
        asset_label = f.get("asset_id") or f.get("protocol")
        if f["match_status"] == "unmatched":
            unmatched.append(asset_label)
            items.append({**f, "quantum_threat": "unknown (no crosswalk match)"})
            continue
        if f["match_status"] == "ambiguous":
            ambiguous.append(asset_label)
        # Use the first match for counting/summary purposes; all matches are retained
        # in the item for a human to disambiguate.
        primary = f["matches"][0]
        threat = primary.get("quantum_threat", "not-vulnerable")
        threat_counts[threat] = threat_counts.get(threat, 0) + 1
        items.append({
            **{k: v for k, v in f.items() if k not in ("matches",)},
            "crosswalk_id": primary["id"],
            "quantum_threat": threat,
            "pqc_replacement": primary.get("pqc_replacement", ""),
            "cnsa2_category": primary.get("cnsa2_category", ""),
            "cnsa2_support_by": primary.get("cnsa2_support_by", ""),
            "cnsa2_exclusive_by": primary.get("cnsa2_exclusive_by", ""),
            "all_matches": [m["id"] for m in f["matches"]],
        })

    return {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "cbom_builder_version": __version__,
        "total_components": len(findings),
        "quantum_threat_counts": threat_counts,
        "unmatched_components": unmatched,
        "ambiguous_components": ambiguous,
        "items": items,
    }


def write_report_json(report, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)


def write_report_csv(path, report):
    fieldnames = ["asset_id", "protocol", "component", "match_status", "crosswalk_id",
                  "quantum_threat", "pqc_replacement", "cnsa2_category",
                  "cnsa2_support_by", "cnsa2_exclusive_by"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for item in report["items"]:
            w.writerow(item)


def text_summary(report):
    lines = [
        f"CBOM report -- generated {report['generated_at']} "
        f"(cbom-builder v{report['cbom_builder_version']})",
        f"Components scanned: {report['total_components']}",
        "",
        "Quantum-threat breakdown:",
    ]
    for threat, count in report["quantum_threat_counts"].items():
        if count:
            lines.append(f"  {threat:20s} {count}")
    if report["unmatched_components"]:
        lines.append("")
        lines.append(f"Unmatched (no crosswalk entry found -- {len(report['unmatched_components'])}):")
        for name in report["unmatched_components"]:
            lines.append(f"  - {name}")
    if report["ambiguous_components"]:
        lines.append("")
        lines.append(f"Ambiguous (multiple crosswalk entries matched -- "
                      f"{len(report['ambiguous_components'])}, first match used):")
        for name in report["ambiguous_components"]:
            lines.append(f"  - {name}")
    lines.append("")
    lines.append("Highest-priority findings (broken-by-shor):")
    for item in report["items"]:
        if item.get("quantum_threat") == "broken-by-shor":
            lines.append(f"  - {item.get('asset_id') or item.get('protocol')}: "
                          f"{item.get('crosswalk_id')} -> {item.get('pqc_replacement')}")
    return "\n".join(lines)
