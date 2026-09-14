import os
import unittest

from cbom_builder.crosswalk import load_crosswalk
from cbom_builder.inventory import load_inventory
from cbom_builder.scanner import InventoryError, scan_inventory

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "sample_inventory.csv")


class TestScanner(unittest.TestCase):
    def test_scan_sample_inventory_matches_known_rows(self):
        crosswalk = load_crosswalk()
        inventory = load_inventory(FIXTURE)
        findings = scan_inventory(inventory, crosswalk)
        self.assertEqual(len(findings), 8)

        by_asset = {f["asset_id"]: f for f in findings}

        self.assertEqual(by_asset["PLC-101"]["match_status"], "matched")
        self.assertEqual(by_asset["PLC-101"]["matches"][0]["id"], "OT-001")
        self.assertEqual(by_asset["PLC-101"]["matches"][0]["quantum_threat"], "no-crypto")

        self.assertEqual(by_asset["HMI-GW-02"]["match_status"], "matched")
        self.assertEqual(by_asset["HMI-GW-02"]["matches"][0]["id"], "OT-006")

        self.assertEqual(by_asset["RTU-204"]["matches"][0]["id"], "OT-003")
        self.assertEqual(by_asset["RTU-205"]["matches"][0]["id"], "OT-004")

        # No crosswalk entry documents this made-up protocol -- must be reported as
        # unmatched, never silently dropped or guessed at.
        self.assertEqual(by_asset["UNKNOWN-DEV-99"]["match_status"], "unmatched")
        self.assertEqual(by_asset["UNKNOWN-DEV-99"]["matches"], [])

    def test_missing_protocol_field_raises(self):
        crosswalk = load_crosswalk()
        with self.assertRaises(InventoryError):
            scan_inventory([{"asset_id": "no-protocol-here"}], crosswalk)

    def test_component_narrows_ambiguous_protocol_matches(self):
        # "OPC UA" alone matches two crosswalk rows (OT-006, OT-007); component should
        # narrow to exactly one.
        crosswalk = load_crosswalk()
        findings = scan_inventory(
            [{"asset_id": "x", "protocol": "OPC UA", "component": "Aes256Sha256RsaPss"}],
            crosswalk,
        )
        self.assertEqual(findings[0]["match_status"], "matched")
        self.assertEqual(findings[0]["matches"][0]["id"], "OT-007")

    def test_protocol_alone_without_component_is_ambiguous_for_opc_ua(self):
        crosswalk = load_crosswalk()
        findings = scan_inventory([{"asset_id": "x", "protocol": "OPC UA"}], crosswalk)
        self.assertEqual(findings[0]["match_status"], "ambiguous")
        self.assertGreaterEqual(len(findings[0]["matches"]), 2)


if __name__ == "__main__":
    unittest.main()
