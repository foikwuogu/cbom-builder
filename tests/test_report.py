import os
import unittest

from cbom_builder.crosswalk import load_crosswalk
from cbom_builder.inventory import load_inventory
from cbom_builder.report import build_report, text_summary
from cbom_builder.scanner import scan_inventory

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "sample_inventory.csv")


class TestReport(unittest.TestCase):
    def test_build_report_counts_and_unmatched(self):
        crosswalk = load_crosswalk()
        inventory = load_inventory(FIXTURE)
        findings = scan_inventory(inventory, crosswalk)
        report = build_report(findings)

        self.assertEqual(report["total_components"], 8)
        self.assertEqual(report["unmatched_components"], ["UNKNOWN-DEV-99"])
        # 4 of the 8 fixture rows map to broken-by-shor entries (HMI-GW-02, RTU-205,
        # FW-SIGN-01, IIOT-EDGE-03); RTU-204 is weakened-by-grover; PLC-101/MGMT-SW-07
        # are no-crypto; UNKNOWN-DEV-99 is unmatched.
        self.assertEqual(report["quantum_threat_counts"]["broken-by-shor"], 4)
        self.assertEqual(report["quantum_threat_counts"]["weakened-by-grover"], 1)
        self.assertEqual(report["quantum_threat_counts"]["no-crypto"], 2)

    def test_text_summary_lists_shor_broken_findings(self):
        crosswalk = load_crosswalk()
        inventory = load_inventory(FIXTURE)
        report = build_report(scan_inventory(inventory, crosswalk))
        summary = text_summary(report)
        self.assertIn("HMI-GW-02", summary)
        self.assertIn("Quantum-threat breakdown", summary)


if __name__ == "__main__":
    unittest.main()
