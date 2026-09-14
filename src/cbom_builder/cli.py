"""Command-line interface for cbom-builder.

    cbom-builder scan inventory.csv --output cbom_report.json
    cbom-builder scan inventory.csv --format text
    cbom-builder parse-cert device.pem
    cbom-builder list-crosswalk
"""

import argparse
import sys

from . import __version__
from .crosswalk import load_crosswalk
from .inventory import load_inventory
from .parsers.x509_parser import parse_certificate_file
from .report import build_report, text_summary, write_report_csv, write_report_json
from .scanner import InventoryError, scan_inventory


def _cmd_scan(args):
    crosswalk = load_crosswalk(args.crosswalk)
    inventory = load_inventory(args.inventory)
    try:
        findings = scan_inventory(inventory, crosswalk)
    except InventoryError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    report = build_report(findings)

    if args.format == "json":
        payload = report
    if args.output:
        if args.format == "csv":
            write_report_csv(args.output, report)
        else:
            write_report_json(report, args.output)
        print(f"wrote {args.format} report to {args.output}")
    if args.format == "text" or not args.output:
        print(text_summary(report))
    return 0


def _cmd_parse_cert(args):
    row = parse_certificate_file(args.certificate, asset_id=args.asset_id)
    crosswalk = load_crosswalk(args.crosswalk)
    findings = scan_inventory([row], crosswalk)
    report = build_report(findings)
    print(text_summary(report))
    if args.output:
        write_report_json(report, args.output)
        print(f"wrote json report to {args.output}")
    return 0


def _cmd_list_crosswalk(args):
    crosswalk = load_crosswalk(args.crosswalk)
    for row in crosswalk:
        print(f"{row['id']:8s} {row['protocol']} -- {row['component']} "
              f"[{row['quantum_threat']}]")
    print(f"\n{len(crosswalk)} entries.")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="cbom-builder", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=f"cbom-builder {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="scan a component inventory against the crosswalk")
    scan.add_argument("inventory", help="path to a .csv or .json inventory file")
    scan.add_argument("--crosswalk", help="path to a custom crosswalk .json "
                       "(default: the crosswalk bundled with the package)")
    scan.add_argument("--output", help="path to write the report to")
    scan.add_argument("--format", choices=["json", "csv", "text"], default="text")
    scan.set_defaults(func=_cmd_scan)

    parse_cert = sub.add_parser("parse-cert", help="parse a PEM certificate and scan it")
    parse_cert.add_argument("certificate", help="path to a PEM certificate file")
    parse_cert.add_argument("--asset-id", help="label for this certificate in the report")
    parse_cert.add_argument("--crosswalk", help="path to a custom crosswalk .json")
    parse_cert.add_argument("--output", help="path to write the JSON report to")
    parse_cert.set_defaults(func=_cmd_parse_cert)

    list_cw = sub.add_parser("list-crosswalk", help="print every crosswalk entry")
    list_cw.add_argument("--crosswalk", help="path to a custom crosswalk .json")
    list_cw.set_defaults(func=_cmd_list_crosswalk)

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
