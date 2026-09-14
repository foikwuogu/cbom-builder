import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from fixtures.certs_fixture import EC_P256_CERT_PEM, RSA_2048_CERT_PEM  # noqa: E402

from cbom_builder.crosswalk import load_crosswalk
from cbom_builder.parsers.x509_parser import parse_certificate
from cbom_builder.scanner import scan_inventory


class TestX509Parser(unittest.TestCase):
    def test_parse_rsa_certificate(self):
        row = parse_certificate(RSA_2048_CERT_PEM)
        self.assertEqual(row["classical_algorithm_observed"], "RSA-2048")
        self.assertEqual(row["key_bits_observed"], "2048")
        self.assertEqual(row["protocol"], "X.509 certificate (generic / protocol-agnostic)")
        self.assertEqual(row["component"], "RSA public key")
        self.assertIn("test-rsa-device", row["asset_id"])

    def test_parse_ec_certificate(self):
        row = parse_certificate(EC_P256_CERT_PEM)
        self.assertIn("ECDSA/ECDH", row["classical_algorithm_observed"])
        self.assertEqual(row["key_bits_observed"], "256")
        self.assertEqual(row["component"], "EC public key (ECDSA/ECDH)")

    def test_parsed_certificate_scans_as_broken_by_shor(self):
        crosswalk = load_crosswalk()
        row = parse_certificate(RSA_2048_CERT_PEM)
        findings = scan_inventory([row], crosswalk)
        self.assertEqual(findings[0]["match_status"], "matched")
        self.assertEqual(findings[0]["matches"][0]["quantum_threat"], "broken-by-shor")
        self.assertEqual(findings[0]["matches"][0]["id"], "OT-014")


if __name__ == "__main__":
    unittest.main()
